import asyncio
import pytest

from camisole.isolate import Isolator
from camisole.languages.python import Python

MAX_BOX_AMOUNT = 5


def build_runners(amount):
    # monkey-patch isolate_conf namedtuple
    Isolator.isolate_conf = (
        Isolator.isolate_conf._replace(max_boxes=MAX_BOX_AMOUNT))
    for test in range(amount):
        yield Python({'source': 'print(42)', 'tests': [{}]}).run()


@pytest.mark.asyncio
@pytest.mark.parametrize('n', range(1, MAX_BOX_AMOUNT + 1))
async def test_just_enough_boxes(n):
    futures = list(build_runners(n))
    done, pending = await asyncio.wait(futures)
    assert not pending
    for coro in done:
        assert coro.result()['tests'][0]['stdout'] == b'42\n'


@pytest.mark.asyncio
@pytest.mark.parametrize('n', range(MAX_BOX_AMOUNT + 1, MAX_BOX_AMOUNT * 2))
async def test_too_many_boxes(n):
    futures = list(build_runners(n))
    done, pending = await asyncio.wait(futures)
    # it is important to retrieve all the exceptions so asyncio is happy
    exceptions = [task.exception() for task in done]
    assert any(isinstance(e, RuntimeError)
               and "No isolate box ID available" in str(e)
               for e in exceptions)
