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

    def __init__(source_data, opts):
        self.source_data = source_data
        self.opts = opts

    async def __aenter__(self):
        self.isolator = camisole.isolate.get_isolator(time_limit=opts[)
        await self.isolator.__aenter__()

        self.wd = Path(self.isolator.path)

        self.compiled = Path(wd) / 'compiled'
        self.source = self.wd / ('source' + self.source_ext)
        self.source.open('w').write(self.source_data)

    async def __aexit__(self, exc, value, tb):
        await self.isolator.__aexit__()

    async def compile(self):
        pass

    async def execute(source, opts):
        pass

    def compile_opt_out(self):
        return ['-o', str(self.compiled)]

    def compile_command(self):
        if self.compiler is None:
            return None
        return ([self.compiler] + self.compile_opts + self.compile_opt_out() +
                [str(self.source)])

    def run_command(self):
        cmd = []
        if self.interpreter is not None:
            cmd += [self.interpreter] + self.interpret_opts
        return cmd + [str(self.compiled)]
