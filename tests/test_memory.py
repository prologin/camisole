import pytest

import camisole.languages


def python_list(n, max_mem=None):
    args = {}
    if max_mem:
        args['execute'] = {'mem': max_mem}
    return camisole.languages.python.Python({
        'tests': [{}],
        'source': 'print(list(range({}))[-1])'.format(n),
        **args
    })


@pytest.mark.asyncio
async def test_no_limit():
    n = int(1e6)
    r = await python_list(n).run()
    assert r['tests'][0]['meta']['status'] == 'OK'
    assert r['tests'][0]['stdout'].strip() == str(n - 1)


@pytest.mark.asyncio
async def test_below_limit():
    n = int(1e5)
    r = await python_list(n, max_mem=50000).run()
    assert r['tests'][0]['meta']['status'] == 'OK'
    assert r['tests'][0]['stdout'].strip() == str(n - 1)


@pytest.mark.asyncio
async def test_above_limit():
    n = int(1e6)
    r = await python_list(n, max_mem=50000).run()
    assert r['tests'][0]['meta']['status'] == 'RUNTIME_ERROR'
    assert r['tests'][0]['stdout'].strip() == ''
    assert 'MemoryError' in r['tests'][0]['stderr']
