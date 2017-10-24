import os
import pytest

from camisole.httpserver import TYPE_JSON, CONTENT_TYPES


@pytest.mark.asyncio
async def test_default(http_client):
    assert "Welcome to Camisole" in (await (await http_client.get('/')).text())


@pytest.mark.asyncio
async def test_run_bad_schema(http_request):
    result = await http_request('/run', {'source': ''})
    assert not result['success']
    message = result['error'].lower()
    assert "malformed payload" in message
    assert ".lang: expected a string, got nothing" in message


@pytest.mark.asyncio
async def test_bad_content_type(http_client):
    result = await (await http_client.post('/run', data=b'bad-stuff')).json()
    assert not result['success']
    assert 'unknown content-type' in result['error'].lower()


@pytest.mark.asyncio
async def test_malformed_input(http_client):
    result = await (await http_client.post(
        '/run', data=b'bad-stuff', headers={'content-type': TYPE_JSON})).json()
    assert not result['success']
    assert f'malformed {TYPE_JSON}' in result['error'].lower()


@pytest.mark.asyncio
@pytest.mark.parametrize('accept', CONTENT_TYPES)
async def test_run_unknown_language(http_request, accept):
    result = await http_request(
        '/run', {'lang': 'foobar', 'source': ''}, accept=accept)
    assert not result['success']
    assert 'incorrect language' in result['error'].lower()


@pytest.mark.asyncio
@pytest.mark.parametrize('accept', CONTENT_TYPES)
async def test_run_str_source_str_stdout_decodes_to_string(http_request,
                                                           accept):
    src = f'import sys; sys.stdout.write("foo")'
    expected = 'foo' if accept == TYPE_JSON else b'foo'
    result = await http_request(
        '/run', {'lang': 'python', 'tests': [{}], 'source': src}, accept=accept)
    assert result['success']
    assert result['tests'][0]['stdout'] == expected


@pytest.mark.asyncio
async def test_run_str_source_bin_stdout_fails_if_json_enforced(http_request):
    expected = b"\xa0\x00\xa0"
    src = f'import sys; sys.stdout.buffer.write({expected!r})'
    result = await http_request(
        '/run', {'lang': 'python', 'tests': [{}], 'source': src},
        accept=TYPE_JSON)
    assert not result['success']
    assert "be able to receive binary" in result['error']


@pytest.mark.asyncio
async def test_run_str_source_bin_stdout_fallsback_to_msgpack(http_request):
    expected = b"\xa0\x00\xa0"
    src = f'import os,sys; sys.stdout.buffer.write({expected!r})'
    result = await http_request(
        '/run', {'lang': 'python', 'tests': [{}], 'source': src})
    assert result['success']
    assert result['tests'][0]['stdout'] == expected


@pytest.mark.asyncio
async def test_run_bin_source_str_stdout_decodes_to_string(msgpack_request):
    src = b'# coding: utf-8\n# \xa0\nprint("foo")'
    result = await msgpack_request(
        '/run', {'lang': 'python', 'tests': [{}], 'source': src})
    assert result['success']
    assert result['tests'][0]['stdout'] == "foo\n"


@pytest.mark.asyncio
async def test_run_bin_source_bin_stdout_decodes_to_bytes(msgpack_request):
    src = (b'# coding: utf-8\n# \xa0\n'
           br'import sys; sys.stdout.buffer.write(b"\xa0\xa0")')
    result = await msgpack_request(
        '/run', {'lang': 'python', 'tests': [{}], 'source': src})
    assert result['success']
    assert result['tests'][0]['stdout'] == b"\xa0\xa0"


@pytest.mark.asyncio
@pytest.mark.parametrize('accept', CONTENT_TYPES)
async def test_run_large_payload(http_request, http_client_large_size, accept):
    test = {'stdin': 'A' * 1024 * 1024 * 1}
    data = {'lang': 'python', 'source': 'print(input())', 'tests': [test]}

    # not OK with default limit
    res = await http_request('/run', data, accept=accept)
    assert not res['success']
    assert 'request entity too large' in res['error'].lower()

    # OK with large limit
    res = await http_request(
        '/run', data, accept=accept, client=http_client_large_size)
    assert res['success']


@pytest.mark.asyncio
@pytest.mark.parametrize('accept', CONTENT_TYPES)
async def test_test(json_request, accept):
    result = await json_request('/test', {}, accept=accept)
    assert result['success']
    assert result['results']['python']['success']


@pytest.mark.asyncio
@pytest.mark.parametrize('accept', CONTENT_TYPES)
async def test_system(json_request, accept):
    result = await json_request('/system', {}, accept=accept)
    assert result['success']
    assert result['system']['cpu_count'] == os.cpu_count()
    assert isinstance(result['system']['cpu_mhz'], float)
    assert isinstance(result['system']['memory'], int)


@pytest.mark.asyncio
@pytest.mark.parametrize('accept', CONTENT_TYPES)
async def test_languages(json_request, accept):
    result = await json_request('/languages', {}, accept=accept)
    assert 'java' in result['languages']
    assert 'programs' in result['languages']['java']
    programs = result['languages']['java']['programs']
    assert 'java' in programs
    assert 'javac' in programs

    assert 'c' in result['languages']
    assert 'programs' in result['languages']['c']
    programs = result['languages']['c']['programs']
    assert '-Wall' in programs['gcc']['opts']
