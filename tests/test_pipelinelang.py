import pytest

from camisole.languages.c import C
from camisole.models import PipelineLang, Lang, Program


class Copy(Lang, register=False):
    source_ext = '.a'
    compiler = Program('cp')

    def compile_command(self, source, output):
        return [self.compiler.cmd,
                self.filter_box_prefix(source),
                self.filter_box_prefix(output)]


class BadCopy(Copy, register=False):
    def compile_command(self, source, output):
        return super().compile_command(source, output + 'bad')


class BadCompiler(Lang, register=False):
    source_ext = '.a'
    compiler = Program('sh', opts=['-c', 'echo BadCompiler is bad >&2'])

    def compile_command(self, source, output):
        return [self.compiler.cmd, *self.compiler.opts]


@pytest.mark.asyncio
async def test_pipeline_success():
    class Pipeline(PipelineLang, register=False):
        sub_langs = [Copy, Copy, C]

    p = Pipeline({'source': C.reference_source, 'tests': [{}]})
    result = await p.run()
    assert result['tests'][0]['stdout'] == b'42\n'


@pytest.mark.asyncio
async def test_pipeline_failure_return_nonzero():
    class Pipeline(PipelineLang, register=False):
        sub_langs = [C, C]

    p = Pipeline({'source': C.reference_source, 'tests': [{}]})
    result = await p.run()
    assert result['compile']['meta']['status'] == 'RUNTIME_ERROR'
    assert result['compile']['meta']['exitcode'] == 1


@pytest.mark.asyncio
async def test_pipeline_failure_does_not_create_binary_while_returning_zero():
    class Pipeline(PipelineLang, register=False):
        sub_langs = [BadCopy, C]

    p = Pipeline({'source': C.reference_source, 'tests': [{}]})
    result = await p.run()
    stderr = result['compile']['stderr'].decode().lower()
    assert 'cannot find result binary' in stderr



@pytest.mark.asyncio
async def test_pipeline_failure_compiler_returns_nonzero():
    class Pipeline(PipelineLang, register=False):
        sub_langs = [BadCompiler, C]

    p = Pipeline({'source': C.reference_source, 'tests': [{}]})
    result = await p.run()
    stderr = result['compile']['stderr'].decode().lower()
    assert 'badcompiler is bad' in stderr
    assert 'cannot find result binary' in stderr
