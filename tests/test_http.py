import json

import aiohttp.web
import asyncio

from camisole.http import make_application


async def get_client(test_client, loop):
    return await test_client(make_application(loop=loop))


async def request(client, data):
    return await (await client.post('/run', data=data)).json()


async def request_test(client, data):
    return await (await client.post('/test', data=data)).json()


async def request_system(client, data):
    return await (await client.post('/system', data=data)).json()


async def request_languages(client):
    return await (await client.post('/languages')).json()


async def test_bad_schema(test_client, loop):
    client = await get_client(test_client, loop)
    result = await request(client, json.dumps({'foo': 'bar'}))
    assert not result['success']
    message = result['error'].lower()
    assert 'failed validating' in message
    assert 'in schema' in message


async def test_bad_json(test_client, loop):
    client = await get_client(test_client, loop)
    result = await request(client, b'bad-stuff')
    assert not result['success']
    assert 'invalid json' in result['error'].lower()


async def test_unknown_language(test_client, loop):
    client = await get_client(test_client, loop)
    result = await request(client, json.dumps({'lang': 'foobar', 'source': ''}))
    assert not result['success']
    assert 'incorrect language' in result['error'].lower()


async def test_simple(test_client, loop):
    # monkey-patch event loop for camisole
    asyncio.set_event_loop(loop)
    client = await get_client(test_client, loop)
    result = await request(client, json.dumps({'lang': 'python',
                                               'source': 'print(42)',
                                               'tests': [{}]}))
    assert result['success']
    assert result['tests'][0]['meta']['status'] == 'OK'
    assert result['tests'][0]['stdout'].strip() == '42'


async def test_test(test_client, loop):
    # monkey-patch event loop for camisole
    asyncio.set_event_loop(loop)
    client = await get_client(test_client, loop)
    result = await request_test(client, json.dumps({}))
    assert result['success']
    assert result['results']['python']['success']


async def test_system(test_client, loop):
    import os
    # monkey-patch event loop for camisole
    asyncio.set_event_loop(loop)
    client = await get_client(test_client, loop)
    result = await request_system(client, json.dumps({}))
    assert result['success']
    assert result['system']['cpu_count'] == os.cpu_count()
    assert isinstance(result['system']['cpu_mhz'], float)
    assert isinstance(result['system']['memory'], int)


async def test_languages(test_client, loop):
    # monkey-patch event loop for camisole
    asyncio.set_event_loop(loop)
    client = await get_client(test_client, loop)
    result = await request_languages(client)
    assert 'programs' in result['languages']['brainfuck']
    programs = result['languages']['brainfuck']['programs']
    assert 'esotope-bfc' in programs
    assert 'gcc' in programs
    assert programs['python2']['version'].startswith('2.7')
    assert '-Wall' in programs['gcc']['opts']
