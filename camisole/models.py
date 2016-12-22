import re
from pathlib import Path

import camisole.isolate


class Lang:
    source_ext = None
    compiler = None
    compile_opts = []
    compile_env = {}
    interpreter = None
    interpret_opts = []
    interpret_env = {}
    version_opt = '--version'
    version_lines = None
    allowed_dirs = []

    def __init__(self, opts):
        self.opts = opts

    async def compile(self):
        if not self.compiler:
            return 0, None, None, None

        isolator = camisole.isolate.get_isolator(
            self.opts.get('compile', {}), allowed_dirs=self.allowed_dirs)
        async with isolator:
            wd = Path(isolator.path)
            source = wd / ('source' + self.source_ext)
            compiled = wd / 'compiled'
            with source.open('w') as sourcefile:
                sourcefile.write(self.opts.get('source', ''))
            cmd = self.compile_command(str(source), str(compiled))
            await isolator.run(cmd, env=self.compile_env)
            binary = self.read_compiled(str(compiled), isolator)

        return (isolator.isolate_retcode, isolator.info, binary)

    async def execute(self, binary, input_data=None):
        if input_data is not None:
            input_data = input_data.encode()
        isolator = camisole.isolate.get_isolator(
            self.opts.get('execute', {}), allowed_dirs=self.allowed_dirs)
        async with isolator:
            wd = isolator.path
            compiled = Path(wd) / self.execute_filename()
            with compiled.open('wb') as c:
                c.write(binary)
            compiled.chmod(0o700)
            await isolator.run(self.execute_command(str(compiled)),
                               env=self.interpret_env,
                               data=input_data)
        return (isolator.isolate_retcode, isolator.info)

    async def run_compilation(self, result):
        if self.compiler is not None:
            cretcode, info, binary = await self.compile()
            result['compile'] = info
            if cretcode != 0:
                return
            if binary is None:
                if result['compile']['stderr'].strip():
                    result['compile']['stderr'] += '\n\n'
                result['compile']['stderr'] += 'Cannot find result binary.\n'
                return
        else:
            binary = self.opts.get('source', '').encode()
        return binary

    async def run_tests(self, binary, result):
        tests = self.opts.get('tests', [])
        if tests:
            result['tests'] = [{}] * len(tests)
        for i, test in enumerate(self.opts.get('tests', [])):
            retcode, info = await self.execute(binary, test.get('stdin'))
            result['tests'][i] = {
                'name': test.get('name', 'test{:03d}'.format(i)),
                **info
            }

            if retcode != 0 and (
                    test.get('fatal', False) or
                    self.opts.get('all_fatal', False)):
                break

    async def run(self):
        result = {}
        binary = await self.run_compilation(result)
        if not binary:
            return result
        await self.run_tests(binary, result)
        return result

    def compile_opt_out(self, output):
        return ['-o', output]

    def read_compiled(self, path, isolator):
        try:
            with Path(path).open('rb') as c:
                return c.read()
        except (FileNotFoundError, PermissionError):
            pass

    def execute_filename(self):
        return 'compiled'

    @staticmethod
    def filter_box_prefix(s):
        return re.sub('/var/(local/)?lib/isolate/[0-9]+', '', s)

    def compile_command(self, source, output):
        if self.compiler is None:
            return None
        return [self.compiler,
                *self.compile_opts,
                *self.compile_opt_out(self.filter_box_prefix(output)),
                self.filter_box_prefix(source)]

    def execute_command(self, output):
        cmd = []
        if self.interpreter is not None:
            cmd += [self.interpreter] + self.interpret_opts
        return cmd + [self.filter_box_prefix(output)]


class PipelineLang(Lang):
    sub_langs = []

    async def run_compilation(self, result):
        source = self.opts.get('source', '')
        for i, lang_cls in enumerate(self.sub_langs):
            lang = lang_cls({**self.opts, 'source': source})
            cretcode, info, binary = await lang.compile()
            result['compile'] = info
            if cretcode != 0:
                return
            if binary is None:
                if result['compile']['stderr'].strip():
                    result['compile']['stderr'] += '\n\n'
                result['compile']['stderr'] += 'Cannot find result binary.\n'
                return
            # compile output is next stage input
            source = binary
            if i < len(self.sub_langs) - 1:
                source = source.decode(errors='ignore')
        return binary

    async def compile(self):
        raise NotImplementedError()
