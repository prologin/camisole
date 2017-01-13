import pytest

import camisole.languages

tolerance = .5


def python_sleep(duration, limit=None):
    args = {}
    if limit:
        args['execute'] = {'wall-time': limit}
    return camisole.languages.python.Python({
        'tests': [{}],
        'source': 'import time; time.sleep({:f})'.format(duration),
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
