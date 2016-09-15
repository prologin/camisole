import aiohttp.web
import json

import camisole.languages

async def run_handler(request):
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        raise aiohttp.errors.HttpBadRequest('Invalid JSON')
    for field in ('lang', 'source'):
        if field not in data:
            raise aiohttp.errors.HttpBadRequest('Field {} not present in JSON'
                    .format(field))

    lang_name = data['lang'].lower()
    try:
        lang = camisole.languages.languages[lang_name](data)
    except KeyError:
        raise aiohttp.errors.HttpBadRequest('Incorrect language {}'
                .format(lang))

    result = await lang.run()
    result = json.dumps(result)
    return aiohttp.web.Response(body=result.encode())


def run():
    app = aiohttp.web.Application()
    app.router.add_route('POST', '/run', run_handler)
    aiohttp.web.run_app(app)
