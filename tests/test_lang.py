import pytest

from camisole.languages.python import Python


@pytest.mark.asyncio
async def test_compile_no_compiler():
    with pytest.raises(RuntimeError):
        await Python({'source': 'print(42)'}).compile()


@pytest.mark.asyncio
async def test_compiler_does_not_create_binary_while_returning_zero():
    class CunningLang(Python, register=False):
        compiler = Python.interpreter

        def python_command(self):
            return 'print("hello", file=open("will.not.be.found", "w"))'

        def compile_command(self, source, output):
            return ([self.compiler.cmd] +
                    self.compiler.opts +
                    ['-c', self.python_command()])

    class VerboseCunningLang(CunningLang, register=False):
        def python_command(self):
            return (super().python_command() +
                    '; import sys; print("hi mom", file=sys.stderr)')

    result = await CunningLang({'source': ''}).run()
    assert 'cannot find result binary' in result['compile']['stderr'].lower()

    result = await VerboseCunningLang({'source': ''}).run()
    assert 'cannot find result binary' in result['compile']['stderr'].lower()
    assert 'hi mom' in result['compile']['stderr'].lower()


@pytest.mark.asyncio
async def test_fatal_test_errors_out():
    result = await Python({'source': '1 / 0', 'tests': [
        {'fatal': False},
        {'fatal': True},
        {'fatal': False},
    ]}).run()
    assert len(result['tests']) == 3
    assert result['tests'][0]['meta']['status'] == 'RUNTIME_ERROR'
    assert result['tests'][1]['meta']['status'] == 'RUNTIME_ERROR'
    assert result['tests'][2] == {}


@pytest.mark.asyncio
async def test_non_fatal_test_errors_out_in_all_fatal_mode():
    result = await Python({'source': '1 / 0', 'all_fatal': True, 'tests': [
        {'fatal': False},
        {'fatal': False},
        {'fatal': False},
    ]}).run()
    assert len(result['tests']) == 3
    assert result['tests'][0]['meta']['status'] == 'RUNTIME_ERROR'
    assert result['tests'][1] == {}
    assert result['tests'][2] == {}


@pytest.mark.asyncio
async def test_input_data():
    echo = 'import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())'
    inputs = ['hello', 'world', 'emoji \U0001F618 face']
    result = await Python({'source': echo, 'tests': [
        {'stdin': stdin} for stdin in inputs
    ]}).run()

    assert len(result['tests']) == len(inputs)
    for test, stdin in zip(result['tests'], inputs):
        assert test['stdout'] == stdin


@pytest.mark.asyncio
async def test_bad_ref():
    from camisole.languages.python import Python
    from camisole.ref import test

    class BadLang(Python):
        reference_source = 'print(43)'

    ok, result = await test('badlang')
    assert not ok


def test_compile_command_with_no_compiler():
    assert (Python({'source': 'print(42)'})
            .compile_command('print(42)', 'test.bin')) is None
