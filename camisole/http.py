import aiohttp
import json

import camisole.models

async def request_handler(request):
    try:
        data = await request.post()
    except json.decoder.JSONDecodeError:
        raise aiohttp.errors.HttpBadRequest('Invalid JSON')
    data = json.loads(data)
    for field in ('lang', 'source'):
        field not in data:
            raise aiohttp.errors.HttpBadRequest('Field {} not present in JSON'
                    .format(field))

    lang_name = data['lang'].lower()
    try:
        lang = camisole.models.languages[lang_name]
    except KeyError:
        raise aiohttp.errors.HttpBadRequest('Incorrect language {}'
                .format(lang))

    source = data['source']
    opts = {
        'time': None,
        'memory': None,
    }
    opts.update({k: v for k, v in source if k in opts})

    result = await lang.execute(source, opts)
    return aiohttp.web.Response(body=result)
