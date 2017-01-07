import pytest

import camisole.languages
from camisole.models import PipelineLang, Lang


class Copy(Lang, register=False):
    source_ext = '.a'
    compiler = '/usr/bin/cp'

    def compile_command(self, source, output):
        return [self.compiler,
                self.filter_box_prefix(source),
                self.filter_box_prefix(output)]


class BadCopy(Copy, register=False):
    def compile_command(self, source, output):
        return super().compile_command(source, output + 'bad')


@pytest.mark.asyncio
async def test_pipeline_success():
    class Pipeline(PipelineLang, register=False):
        sub_langs = [Copy, Copy, camisole.languages.C]

    p = Pipeline({'source': '#include <stdio.h>\nint main(void) { printf("42\\n"); return 0; }', 'tests': [{}]})
    result = await p.run()
    assert result['tests'][0]['stdout'] == '42\n'


@pytest.mark.asyncio
async def test_pipeline_failure_return_nonzero():
    class Pipeline(PipelineLang, register=False):
        sub_langs = [camisole.languages.C, camisole.languages.C]

    p = Pipeline({'source': '#include <stdio.h>\nint main(void) { printf("42\\n"); return 0; }', 'tests': [{}]})
    result = await p.run()
    assert result['compile']['meta']['status'] == 'RUNTIME_ERROR'
    assert result['compile']['meta']['exitcode'] == 1


@pytest.mark.asyncio
async def test_pipeline_failure_does_not_create_binary_while_returning_zero():
    class Pipeline(PipelineLang, register=False):
        sub_langs = [BadCopy, camisole.languages.C]

    p = Pipeline({'source': '#include <stdio.h>\nint main(void) { printf("42\\n"); return 0; }', 'tests': [{}]})
    result = await p.run()
    assert 'cannot find result binary' in result['compile']['stderr'].lower()
