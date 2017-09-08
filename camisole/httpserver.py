import aiohttp.web
import functools
import json
import jsonschema
import msgpack
import traceback

from camisole.utils import AcceptHeader
import camisole.languages
import camisole.ref
import camisole.schema
import camisole.system

TYPE_JSON = 'application/json'
TYPE_MSGPACK = 'application/msgpack'
CONTENT_TYPES = (TYPE_JSON, TYPE_MSGPACK)


class BinaryJsonEncoder(json.JSONEncoder):
    """Best-effort :class:`JSONEncoder` that tries to decode bytes."""

    def default(self, o):
        if isinstance(o, bytes):
            try:
                return o.decode()
            except UnicodeDecodeError:
                raise TypeError() from None
        return super().default(o)


def json_msgpack_handler(wrapped):
    @functools.wraps(wrapped)
    async def wrapper(request):
        accepted_types = list(AcceptHeader.get_best_accepted_types(
            request.headers.getone('accept', '*/*'), CONTENT_TYPES))
        content_type = request.headers.getone('content-type', TYPE_JSON)

        def encoder_for(content_type):
            if content_type == TYPE_JSON:
                return lambda e: json.dumps(
                    e, cls=BinaryJsonEncoder, sort_keys=True).encode()
            elif content_type == TYPE_MSGPACK:
                return functools.partial(msgpack.dumps, use_bin_type=True)

        def response(payload, cls=aiohttp.web.Response):
            for content_type in accepted_types:
                try:
                    data = encoder_for(content_type)(payload)
                except Exception:
                    continue
                return cls(body=data, content_type=content_type)
            # no acceptable content type
            cls = aiohttp.web.HTTPNotAcceptable
            if TYPE_MSGPACK not in accepted_types:
                # explain how to work around the issue
                return error(
                    cls, f"use 'Accept: {TYPE_MSGPACK}' to be able to receive "
                         f"binary payloads")
            # no encoder can work
            raise cls()

        def error(cls, msg):
            return response({'success': False, 'error': msg}, cls=cls)

        if content_type == TYPE_JSON:
            decoder = lambda e: json.loads(e.decode())
        elif content_type == TYPE_MSGPACK:
            decoder = functools.partial(msgpack.loads, encoding='utf-8')
        else:
            return error(aiohttp.web.HTTPUnsupportedMediaType,
                         f"unknown content-type {content_type}")

        try:
            data = await request.read()
        except aiohttp.web.HTTPClientError as e:
            return error(e.__class__, str(e))
        except Exception:
            return error(
                aiohttp.web.HTTPInternalServerError, traceback.format_exc())

        try:
            data = decoder(data) if data else {}
        except Exception:
            return error(
                aiohttp.web.HTTPBadRequest, f"malformed {content_type}")

        try:
            # actually execute handler
            result = await wrapped(request, data)
        except Exception:
            return error(
                aiohttp.web.HTTPInternalServerError, traceback.format_exc())

        return response({'success': True, **result})

    return wrapper


@json_msgpack_handler
async def run_handler(request, data):
    try:
        camisole.schema.validate(data)
    except jsonschema.exceptions.ValidationError as e:
        return {'success': False, 'error': f"malformed payload: {e.message}"}

    lang_name = data['lang'].lower()
    try:
        lang = camisole.languages.by_name(lang_name)(data)
    except KeyError:
        raise RuntimeError('Incorrect language {}'.format(lang_name))

    return await lang.run()


@json_msgpack_handler
async def test_handler(request, data):
    langs = camisole.languages.all().keys()
    langs -= set(data.get('exclude', []))

    results = {name: {'success': success, 'raw': raw}
               for name in langs
               for success, raw in [await camisole.ref.test(name)]}
    return {'results': results}


@json_msgpack_handler
async def system_handler(request, data):
    return {'system': camisole.system.info()}


@json_msgpack_handler
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
    from camisole.conf import conf
    app = make_application(client_max_size=conf['max-body-size'])
    aiohttp.web.run_app(app, **kwargs)
