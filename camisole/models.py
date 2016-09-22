import re
from pathlib import Path

import camisole.isolate

class Lang:
    source_ext = None
    compiler = None
    compile_opts = []
    interpreter = None
    interpret_opts = []
    version_opt = '--version'
    version_lines = None

    def __init__(self, opts):
        self.opts = opts

    async def compile(self):
        if not self.compiler:
            return 0, None, None, None

        isolator = camisole.isolate.get_isolator(self.opts.get('compile', {}))
        async with isolator:
            wd = Path(isolator.path)
            source = wd / ('source' + self.source_ext)
            compiled = wd / 'compiled'

            with source.open('w') as sourcefile:
                sourcefile.write(self.opts.get('source', ''))
            cmd = self.compile_command(str(source), str(compiled))
            await isolator.run(cmd)
            try:
                with compiled.open('rb') as c:
                    compiled = c.read()
            except (FileNotFoundError, PermissionError):
                compiled = None
        return (isolator.isolate_retcode, isolator.info, compiled)

    async def execute(self, binary, input_data=None):
        if input_data is not None:
            input_data = input_data.encode()
        isolator = camisole.isolate.get_isolator(self.opts.get('execute', {}))
        async with isolator:
            wd = isolator.path
            compiled = Path(wd) / 'compiled'
            with compiled.open('wb') as c:
                c.write(binary)
            compiled.chmod(0o700)
            await isolator.run(self.execute_command(str(compiled)),
                    data=input_data)
        return (isolator.isolate_retcode, isolator.info)

    async def run(self):
        result = {}
        if self.compiler is not None:
            cretcode, info, binary = await self.compile()
            result['compile'] = info
            if cretcode != 0:
                return result
            if binary is None:
                if result['compile']['stderr'].strip():
                    result['compile']['stderr'] += '\n\n'
                result['compile']['stderr'] += 'Cannot find result binary.\n'
                return result
        else:
            binary = self.opts.get('source', '').encode()

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

        return result

    def compile_opt_out(self, output):
        return ['-o', output]

    def filter_box_prefix(self, s):
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
