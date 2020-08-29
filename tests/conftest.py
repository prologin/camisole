import msgpack
import pytest

from aiohttp.test_utils import BaseTestServer, TestServer, TestClient
from aiohttp.web import Application

from camisole.httpserver import make_application

# load builtins once and for all
from camisole.languages import load_builtins
load_builtins()


@pytest.yield_fixture
def aio_client(event_loop):
    """
    Copied from aiohttp/aiohttp/pytest_plugin.py
    """
    clients = []

    async def go(__param, *args, server_kwargs={}, **kwargs):

        if callable(__param) and \
                not isinstance(__param, (Application, BaseTestServer)):
            __param = __param(event_loop, *args, **kwargs)
            kwargs = {}
        else:
            assert not args, "args should be empty"

        if isinstance(__param, Application):
            server = TestServer(__param, **server_kwargs)
            client = TestClient(server, **kwargs)
        elif isinstance(__param, BaseTestServer):
            client = TestClient(__param, **kwargs)
        else:
            raise ValueError("Unknown argument type: %r" % type(__param))

        await client.start_server()
        clients.append(client)
        return client

    yield go

    async def finalize():
        while clients:
            await clients.pop().close()

    event_loop.run_until_complete(finalize())


@pytest.fixture
async def http_client(aio_client):
    app = make_application(client_max_size=1024 * 1)
    return await aio_client(app)


@pytest.fixture
async def http_client_large_size(aio_client):
    app = make_application(client_max_size=1024 * 100)
    return await aio_client(app)


async def http_response_decode(response):
    content_type = response.headers.get('content-type', '')
    if content_type.endswith('json'):
        return await response.json()
    elif content_type.endswith('msgpack'):
        return msgpack.loads(await response.read(), raw=False)
    else:
        return await response.read()


@pytest.fixture(params=['json', 'msgpack'])
def http_request(request):
    if request.param == 'json':
        return request.getfixturevalue('json_request')
    if request.param == 'msgpack':
        pytest.importorskip('msgpack')
        return request.getfixturevalue('msgpack_request')


@pytest.fixture
def json_request(http_client):
    default_client = http_client

    async def call(url, json=None, client=None, accept='*/*'):
        if not client:
            client = default_client
        method = client.post if json is not None else client.get
        resp = await method(url, json=json, headers={'accept': accept})
        return await http_response_decode(resp)

    return call


@pytest.fixture
def msgpack_request(http_client):
    default_client = http_client

    async def call(url, data=None, client=None, accept='*/*'):
        if not client:
            client = default_client
        method = client.post if data is not None else client.get
        resp = await method(
            url,
            data=msgpack.dumps(data, use_bin_type=True),
            headers={'content-type': 'application/msgpack', 'accept': accept})
        return await http_response_decode(resp)

    return call
