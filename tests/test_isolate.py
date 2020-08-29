import pytest

import camisole.isolate


@pytest.mark.asyncio
async def test_stdout_stderr():
    isolator = camisole.isolate.Isolator({})
    async with isolator:
        await isolator.run(['/bin/bash', '-c', 'echo out; echo err >&2'])
    assert isolator.info['stdout'] == b'out\n'
    assert isolator.info['stderr'] == b'err\n'


@pytest.mark.asyncio
async def test_merge_outputs():
    isolator = camisole.isolate.Isolator({})
    async with isolator:
        await isolator.run(['/bin/bash', '-c',
                            'echo a >&2; echo b; echo a >&2; echo b'],
                           merge_outputs=True)
    assert isolator.info['stdout'] == b'a\nb\na\nb\n'
    assert isolator.info['stderr'] == b''


@pytest.mark.asyncio
async def test_invalid_binary():
    isolator = camisole.isolate.Isolator({})
    with pytest.raises(camisole.isolate.IsolateInternalError):
        async with isolator:
            await isolator.run(['/bin/thisdoesntexist', '-c', 'test'])
    assert b'No such file or directory' in isolator.isolate_stderr
    assert b'execve' in isolator.isolate_stderr


# TODO: test a lot of error cases!
