import asyncio
import collections
import pytest

from aiohttp.test_utils import BaseTestServer, TestServer, TestClient
from aiohttp.web import Application

from camisole.http import make_application


def pytest_configure(config):
    import os
    from camisole.languages.java import Java
    from camisole.languages.php import  PHP
    if os.environ.get('TEST_DEBIAN_MODE'):
        Java.allowed_dirs += ['/etc/alternatives']
        PHP.allowed_dirs += ['/etc/alternatives']


@pytest.yield_fixture
def aio_client(event_loop):
    """
    Copied from aiohttp/aiohttp/pytest_plugin.py
    """
    clients = []

    @asyncio.coroutine
    def go(__param, *args, server_kwargs={}, **kwargs):

        if isinstance(__param, collections.Callable) and \
                not isinstance(__param, (Application, BaseTestServer)):
            __param = __param(event_loop, *args, **kwargs)
            kwargs = {}
        else:
            assert not args, "args should be empty"

        if isinstance(__param, Application):
            server = TestServer(__param, loop=event_loop, **server_kwargs)
            client = TestClient(server, loop=event_loop, **kwargs)
        elif isinstance(__param, BaseTestServer):
            client = TestClient(__param, loop=event_loop, **kwargs)
        else:
            raise ValueError("Unknown argument type: %r" % type(__param))

        yield from client.start_server()
        clients.append(client)
        return client

    yield go

    @asyncio.coroutine
    def finalize():
        while clients:
            yield from clients.pop().close()

    event_loop.run_until_complete(finalize())


@pytest.fixture
async def http_client(aio_client, event_loop):
    app = make_application(loop=event_loop)
    return await aio_client(app)


@pytest.fixture
async def http_client_large_size(aio_client, event_loop):
    app = make_application(loop=event_loop, client_max_size=1024 * 1024 * 2)
    return await aio_client(app)


@pytest.fixture
def http_request(http_client):
    default_client = http_client

    async def call(url, json=None, client=None):
        if not client:
            client = default_client
        method = client.post if json is not None else client.get
        resp = await method(url, json=json)
        return await (resp.json if json is not None else resp.text)()

    return call
