import os
import pytest

import camisole.languages
camisole.languages._import_builtins()


@pytest.mark.asyncio
async def test_default(http_request):
    assert "Welcome to Camisole" in (await http_request('/'))


@pytest.mark.asyncio
async def test_run_bad_schema(http_request):
    result = await http_request('/run', {'foo': 'bar'})
    assert not result['success']
    message = result['error'].lower()
    assert 'failed validating' in message
    assert 'in schema' in message


@pytest.mark.asyncio
async def test_fuck_you(http_client):
    result = await (await http_client.post('/run', data=b'bad-stuff')).json()
    assert not result['success']
    assert 'invalid json' in result['error'].lower()


@pytest.mark.asyncio
async def test_run_unknown_language(http_request):
    result = await http_request('/run', {'lang': 'foobar', 'source': ''})
    assert not result['success']
    assert 'incorrect language' in result['error'].lower()


@pytest.mark.asyncio
async def test_run_simple(http_request):
    result = await http_request(
        '/run', {'lang': 'python', 'source': 'print(42)', 'tests': [{}]})
    assert result['success']
    assert result['tests'][0]['meta']['status'] == 'OK'
    assert result['tests'][0]['stdout'].strip() == '42'


@pytest.mark.asyncio
async def test_run_large_payload(http_request, http_client_large_size):
    test = {'stdin': 'A' * 1024 * 1024 * 1}
    data = {'lang': 'python', 'source': 'print(input())', 'tests': [test]}

    # not OK with default limit
    res = await http_request('/run', data)
    assert not res['success']
    assert 'HTTPRequestEntityTooLarge' in res['error']

    # OK with large limit
    res = await http_request('/run', data, client=http_client_large_size)
    assert res['success']


@pytest.mark.asyncio
async def test_test(http_request):
    result = await http_request('/test', {})
    assert result['success']
    assert result['results']['python']['success']


@pytest.mark.asyncio
async def test_system(http_request):
    result = await http_request('/system', {})
    assert result['success']
    assert result['system']['cpu_count'] == os.cpu_count()
    assert isinstance(result['system']['cpu_mhz'], float)
    assert isinstance(result['system']['memory'], int)


@pytest.mark.asyncio
async def test_languages(http_request):
    result = await http_request('/languages', {})
    assert 'programs' in result['languages']['brainfuck']
    programs = result['languages']['brainfuck']['programs']
    assert 'esotope-bfc' in programs
    assert 'gcc' in programs
    assert programs['python2']['version'].startswith('2.7')
    assert '-Wall' in programs['gcc']['opts']
