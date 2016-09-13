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
    async def __aexit__(self, exc, value, tb):
        await self.isolator.__aexit__()

    async def compile(self):
        if not self.compiler:
            return 0, None, None, None

        isolator = camisole.isolate.get_isolator()
        with isolator:
            wd = Path(isolator.path)
            source = wd / ('source' + self.source_ext)
            compiled = wd / 'compiled'

            source.open('w').write(self.source_data)
            cmd = self.compile_command(str(source), str(compiled))
            await self.isolator.run(cmd)
            return (isolator.retcode,
                    isolator.stdout,
                    isolator.stderr,
                    isolator.meta,
                    compiled.read())

    async def execute(self, compiled):
        isolator = camisole.isolate.get_isolator()
        with isolator:
            wd = isolator.path
            compiled = Path(wd) / 'compiled'
            await self.isolator.run(self.execute_command(str(compiled)))
            return (isolator.retcode,
                    isolator.stdout,
                    isolator.stderr,
                    isolator.meta)

    async def run():
        if self.compiler is not None:
            cretcode, cstdout, cstderr, cmeta, binary = await self.compile()
            if cretcode != 0:
                return None #TODO
        retcode, stdout, stderr, meta, binary = await self.execute(binary)
        return None #TODO

    def compile_opt_out(self, output):
        return ['-o', output]

    def compile_command(self, source, output):
        if self.compiler is None:
            return None
        return [self.compiler,
                *self.compile_opts,
                *self.compile_opt_out(output),
                source]

    def execute_command(self, output):
        cmd = []
        if self.interpreter is not None:
            cmd += [self.interpreter] + self.interpret_opts
        return cmd + [output]
