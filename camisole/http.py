import aiohttp.web
import functools
import json
import jsonschema
import traceback

import camisole.languages
import camisole.ref
import camisole.schema
import camisole.system


def json_handler(wrapped):
    @functools.wraps(wrapped)
    async def wrapper(request):
        # XXX: hack no longer needed in recent aiohttp versions
        if not hasattr(request, 'query'):
            import urllib.parse
            request.query = urllib.parse.parse_qs(request.query_string,
                                                  keep_blank_values=True)
            request.query = {k: v[-1] for k, v in request.query.items()}

        try:
            try:
                data = await request.text()
                data = json.loads(data) if data else {}
            except json.decoder.JSONDecodeError:
                raise RuntimeError('Invalid JSON')
            result = await wrapped(request, data)
        except Exception:
            result = {'success': False, 'error': traceback.format_exc()}
        else:
            result = {'success': True, **result}

        pretty = ('pretty' in request.query
                  and request.query['pretty'].lower() in ('', 'true', '1'))
        indent = 4 if pretty else None
        result = json.dumps(result, sort_keys=True, indent=indent)
        return aiohttp.web.Response(body=result.encode(),
                                    content_type='application/json')
    return wrapper


@json_handler
async def run_handler(request, data):
    try:
        camisole.schema.validate(data)
    except jsonschema.exceptions.ValidationError as e:
        return {'success': False, 'error': str(e)}

    lang_name = data['lang'].lower()
    try:
        lang = camisole.languages.by_name(lang_name)(data)
    except KeyError:
        raise RuntimeError('Incorrect language {}'.format(lang_name))

    return await lang.run()


@json_handler
async def test_handler(request, data):
    langs = camisole.languages.all().keys()
    langs -= set(data.get('exclude', []))

    results = {name: {'success': success, 'raw': raw}
               for name in langs
               for success, raw in [await camisole.ref.test(name)]}
    return {'results': results}


@json_handler
async def system_handler(request, data):
    return {'system': camisole.system.info()}


@json_handler
async def languages_handler(request, data):
    return {'languages': {lang: {'name': cls.name, 'programs': cls.programs()}
            for lang, cls in camisole.languages.all().items()}}

async def default_handler(request):
    return aiohttp.web.Response(
        text="Welcome to Camisole. Use the /run endpoint to run some code!\n")


def make_application(**kwargs):
    app = aiohttp.web.Application(**kwargs)
    app.router.add_route('POST', '/run', run_handler)
    app.router.add_route('*', '/', default_handler)
    app.router.add_route('*', '/languages', languages_handler)
    app.router.add_route('*', '/system', system_handler)
    app.router.add_route('*', '/test', test_handler)
    return app


def run(**kwargs):  # noqa
    app = make_application()
    aiohttp.web.run_app(app, **kwargs)
