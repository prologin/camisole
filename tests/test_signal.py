import pytest

from camisole.languages import by_name


@pytest.mark.asyncio
@pytest.mark.parametrize("source_and_signal", (
    ('int a = 0; return 1 / a;', 4, "Illegal instruction"),
    ('volatile int a = 0; return 1 / a;', 8, "Floating point exception"),
))
async def test_signal_message(source_and_signal):
    source, signal, messages = source_and_signal
    source = "int main() { %s }" % source
    result = await by_name('c')({'source': source, 'tests': [{}]}).run()
    test = result['tests'][0]
    assert test['exitcode'] == 1
    assert test['meta']['message'] == f"Caught fatal signal {signal}"
    assert test['meta']['exitsig'] == signal
    assert test['meta']['exitsig-message'] == messages
