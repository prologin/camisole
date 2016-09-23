import asyncio

import pytest

from camisole import isolate
from camisole.languages import Python

MAX_BOX_AMOUNT = 5


def build_runners(amount):
    isolate.get_isolator = isolate.IsolatorFactory(max_box_id=MAX_BOX_AMOUNT)
    for test in range(amount):
        yield Python({'source': 'print(42)', 'tests': [{}]}).run()


@pytest.mark.asyncio
async def test_just_enough_boxes():
    futures = list(build_runners(MAX_BOX_AMOUNT))
    await asyncio.wait(futures)


@pytest.mark.asyncio
async def test_too_many_boxes():
    futures = list(build_runners(MAX_BOX_AMOUNT * 2))
    done, pending = await asyncio.wait(futures)
    # it is important to retrieve all the exceptions so asyncio is happy
    exceptions = [task.exception() for task in done]
    assert any(isinstance(e, RuntimeError)
               and "No isolate box ID available." in str(e)
               for e in exceptions)
