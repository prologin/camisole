import pytest

from camisole.languages.python import Python

# fsize quota needs ext filesystem
pytestmark = pytest.mark.ext4


def python_file(n, fsize=None):
    args = {}
    if fsize:
        args['execute'] = {'fsize': fsize}
    src = f'with open("foo", "w") as f: f.write("A" * {n * 1000})\nprint("OK")'
    return Python({'tests': [{}], 'source': src, **args})


@pytest.mark.asyncio
async def test_without_fsize():
    r = await python_file(100).run()
    assert r['tests'][0]['meta']['status'] == 'OK'
    assert r['tests'][0]['stdout'].strip() == b'OK'


@pytest.mark.asyncio
async def test_with_large_enough_fsize():
    r = await python_file(10, fsize=11).run()
    assert r['tests'][0]['meta']['status'] == 'OK'
    assert r['tests'][0]['stdout'].strip() == b'OK'


@pytest.mark.asyncio
async def test_with_too_small_fsize():
    r = await python_file(10, fsize=9).run()
    assert r['tests'][0]['meta']['status'] != 'OK'
    assert r['tests'][0]['stdout'].strip() != b'OK'
