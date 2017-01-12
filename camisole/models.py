# This file is part of Camisole.
#
# Copyright (c) 2016 Antoine Pietri <antoine.pietri@prologin.org>
# Copyright (c) 2016 Alexandre Macabies <alexandre.macabies@prologin.org>
# Copyright (c) 2016 Association Prologin <info@prologin.org>
#
# Camisole is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prologin-SADM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Prologin-SADM.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import tempfile
import warnings
from pathlib import Path

import camisole.isolate


class Lang:
    _registry = {}

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
    extra_binaries = set()

    def __init_subclass__(cls, register=True, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.name = name or cls.__name__
        if not register:
            return
        registry_name = cls.name.lower()
        if registry_name in cls._registry:
            full_name = lambda c: c.__module__ + '.' + c.__qualname__
            warnings.warn(f"Lang registry: name '{registry_name}' for "
                          f"{full_name(cls)} overwrites "
                          f"{full_name(Lang._registry[registry_name])}")
        cls._registry[registry_name] = cls

    def __init__(self, opts):
        self.opts = opts

    @classmethod
    def required_binaries(cls):
        if cls.compiler:
            yield cls.compiler
        if cls.interpreter:
            yield cls.interpreter
        yield from cls.extra_binaries

    async def compile(self):
        if not self.compiler:
            return 0, None, None, None

        # We give compilers a nice /tmp playground
        root_tmp = tempfile.TemporaryDirectory(prefix='camisole-tmp-')
        os.chmod(root_tmp.name, 0o777)
        tmparg = ['/tmp=' + root_tmp.name + ':rw']

        isolator = camisole.isolate.get_isolator(
            self.opts.get('compile', {}),
            allowed_dirs=self.allowed_dirs + tmparg)
        async with isolator:
            wd = Path(isolator.path)
            source = wd / ('source' + self.source_ext)
            compiled = wd / 'compiled'
            with source.open('w') as sourcefile:
                sourcefile.write(self.opts.get('source', ''))
            cmd = self.compile_command(str(source), str(compiled))
            await isolator.run(cmd, env=self.compile_env)
            binary = self.read_compiled(str(compiled), isolator)

        root_tmp.cleanup()

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


class PipelineLang(Lang, register=False):
    sub_langs = []

    @classmethod
    def required_binaries(cls):
        yield from super().required_binaries()
        for sub in cls.sub_langs:
            yield from sub.required_binaries()

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
