import pytest

import camisole.languages

tolerance = .5


def python_sleep(duration, global_limit=None, local_limit=None):
    args = {'tests': [{}], 'execute': {}}
    if global_limit:
        args['execute']['wall-time'] = global_limit
    if local_limit:
        args['tests'][0]['wall-time'] = local_limit
    return camisole.languages.python.Python({
        'source': f'import time; time.sleep({duration:f})',
        **args
    })


@pytest.mark.asyncio
async def test_no_limit():
    duration = .5
    r = await python_sleep(duration).run()
    test = r['tests'][0]['meta']
    assert test['status'] == 'OK'
    assert abs(test['time-wall'] - duration) < tolerance


@pytest.mark.asyncio
async def test_below_limit():
    duration = .5
    limit = .8
    r = await python_sleep(duration, limit).run()
    test = r['tests'][0]['meta']
    assert test['status'] == 'OK'
    assert abs(test['time-wall'] - limit) < tolerance


@pytest.mark.asyncio
async def test_above_limit():
    duration = 1.
    limit = .8
    r = await python_sleep(duration, limit).run()
    test = r['tests'][0]['meta']
    assert test['status'] == 'TIMED_OUT'
    assert abs(test['time-wall'] - limit) < tolerance
    assert "time limit exceeded" in test['message'].lower()


@pytest.mark.asyncio
async def test_local_limit_stricter():
    duration = 1.
    glimit = 2
    llimit = .8
    r = await python_sleep(duration, glimit, llimit).run()
    test = r['tests'][0]['meta']
    assert test['status'] == 'TIMED_OUT'
    assert abs(test['time-wall'] - llimit) < tolerance
    assert "time limit exceeded" in test['message'].lower()


@pytest.mark.asyncio
async def test_local_limit_larger():
    duration = .5
    glimit = .2
    llimit = .8
    r = await python_sleep(duration, glimit, llimit).run()
    test = r['tests'][0]['meta']
    assert test['status'] == 'OK'
    assert abs(test['time-wall'] - llimit) < tolerance
