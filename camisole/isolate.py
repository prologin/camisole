# This file is part of Camisole.
#
# Copyright (c) 2016 Antoine Pietri <antoine.pietri@prologin.org>
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

import asyncio
import itertools
import pathlib
import tempfile

async def communicate(self, cmdline, data=None, **kwargs):
    proc = await asyncio.create_subprocess_exec(
        *cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, **kwargs)
    stdout, stderr = await proc.communicate(data)
    retcode = await proc.wait()
    return retcode, stdout, stderr


class IsolatorFactory:
    def __init__(self, max_box_id=99):
        self.max_box_id = max_box_id
        self.available_box_id = set(range(max_box_id + 1))

    def __call__(self, *args, **kwargs):
        try:
            curr_id = self.available_box_id.pop()
        except KeyError:
            raise RuntimeError("No isolate box ID available.")
        else:
            return Isolator(curr_id, *args, restore_id_cb=self.restore_id,
                            **kwargs)

    def restore_id(self, box_id):
        if box_id not in range(max_box_id + 1):
            raise RuntimeError("Trying to restore box id {} outside of id "
                               "range.".format(box_id))
        self.available_box_id.add(box_id)


class Isolator:
    def __init__(self, box_id, time_limit=None, wall_time_limit=None,
                 mem_limit=None, fsize_limit=None,
                 allowed_dirs=None, processes=1, file_restore_id_cb=None):
        self.box_id = box_id
        self.time_limit = time_limit
        self.wall_time_limit = wall_time_limit
        self.mem_limit = mem_limit
        self.fsize_limit = fsize_limit
        self.allowed_dirs = allowed_dirs if allowed_dirs is not None else []
        self.processes = processes
        self.box_path = None
        self.restore_id_cb = restore_id_cb
        self.cmd_base = ['isolate', '--box-id', str(box_id), '--cg']

        # Directory containing all the info of the program
        self.meta_file = tempfile.NamedTemporaryFile()
        self.stdout_file = '._stdout'
        self.stderr_file = '._stderr'

        # Cache the result of the program
        self._stdout = None
        self._stderr = None
        self._meta = None

        # Result of the isolate binary
        self.isolate_retcode = None
        self.isolate_stdout = None
        self.isolate_stderr = None


    async def init(self):
        cmd_init = self.cmd_base + ['--init']
        retcode, stdout, _ = await communicate(cmd_init)
        self.path = pathlib.Path(stdout)
        return self.path

    async def cleanup(self):
        cmd_cleanup = self.cmd_base + ['--cleanup']
        await communicate(cmd_init)
        if self.restore_id_cb is not None:
            self.restore_id_cb(self.box_id)
        self.info_dir.cleanup()

    async def run(self, cmdline, data=None, **kwargs):
        cmd_run = self.cmd_base
        cmd_run += list(itertools.chain(*[('-d', d) for d in allowed_dirs]))

        if self.mem_limit is not None:
            cmd_run += ['--mem', str(self.mem_limit)]
        if self.time_limit is not None:
            cmd_run += ['--time', str(self.time_limit)]
        if self.wall_time_limit is not None:
            cmd_run += ['--wall-time', str(self.wall_time_limit)]
        if self.fsize_limit is not None:
            cmd_run += ['--fsize', str(self.fsize_limit)]

        cmd_run += [
            '--meta={}'.format(self.meta_file.name),
            '--stdout={}'.format(self.stdout_file),
            '--stderr={}'.format(self.stderr_file),
            '--processes={}'.format(str(processes)),
            '--run', '--'
        ]
        cmd_run += cmdline

        self.isolate_retcode, self.isolate_stdout, self.isolate_stderr = (
            await communicate(cmd_run, data=data, **kwargs))

    @property
    def meta(self):
        if self._meta is None:
            meta_content = (l.strip() for l in self.meta_file.open())
            self._meta = dict(l.split(':') for l in meta_content if l)
        return self._meta

    @property
    def stdout(self):
        if self._stdout is None:
            path = self.path / 'box' / self.stdout_file
            self._stdout = path.open().read()
        return self._stdout

    @property
    def stderr(self):
        if self._stderr is None:
            path = self.path / 'box' / self.stderr_file
            self._stderr = path.open().read()
        return self._stderr


get_isolator = IsolatorFactory()
