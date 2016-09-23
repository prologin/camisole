import aiohttp.web
import functools
import json

import camisole.languages


def json_handler(wrapped):
    @functools.wraps(wrapped)
    async def wrapper(request):
        try:
            try:
                data = await request.json()
            except json.decoder.JSONDecodeError:
                raise RuntimeError('Invalid JSON')
            result = await wrapped(data)
        except Exception as e:
            result = {'success': False, 'error': str(e)}
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
        lang = camisole.languages.languages[lang_name](data)
    except KeyError:
        raise RuntimeError('Incorrect language {}'.format(lang_name))

    return await lang.run()


def run(**kwargs):  # noqa
    app = aiohttp.web.Application()
    app.router.add_route('POST', '/run', run_handler)
    aiohttp.web.run_app(app, **kwargs)
