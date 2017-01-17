import aiohttp.web
import functools
import json
import traceback

import camisole.languages
import camisole.ref
import camisole.system


def json_handler(wrapped):
    @functools.wraps(wrapped)
    async def wrapper(request):
        try:
            try:
                data = await request.text()
                data = json.loads(data) if data else {}
            except json.decoder.JSONDecodeError:
                raise RuntimeError('Invalid JSON')
            result = await wrapped(data)
        except Exception:
            result = {'success': False, 'error': traceback.format_exc()}
        else:
            result = {'success': True, **result}
        result = json.dumps(result)
        return aiohttp.web.Response(body=result.encode(),
                                    content_type='application/json')
    return wrapper


@json_handler
async def run_handler(data):
    for field in ('lang', 'source'):
        if field not in data:
            raise RuntimeError('Field {} not present in JSON'.format(field))

    lang_name = data['lang'].lower()
    try:
        lang = camisole.languages.by_name(lang_name)(data)
    except KeyError:
        raise RuntimeError('Incorrect language {}'.format(lang_name))

    return await lang.run()


@json_handler
async def test_handler(data):
    langs = camisole.languages.all().keys()
    langs -= set(data.get('exclude', []))

    results = {name: {'success': success, 'raw': raw}
               for name in langs
               for success, raw in [await camisole.ref.test(name)]}
    return {'results': results}


@json_handler
async def system_handler(data):
    return {'system': camisole.system.info()}


def make_application(**kwargs):
    app = aiohttp.web.Application(**kwargs)
    app.router.add_route('POST', '/run', run_handler)
    app.router.add_route('*', '/test', test_handler)
    app.router.add_route('*', '/system', system_handler)
    return app


def run(**kwargs):  # noqa
    app = make_application()
    aiohttp.web.run_app(app, **kwargs)
