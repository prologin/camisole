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

async def communicate(self, cmdline, data=None, **kwargs):
    proc = await asyncio.create_subprocess_exec(
        *cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, **kwargs)
    stdout, stderr = await proc.communicate(data)
    retcode = await proc.wait()
    return retcode, stdout, stderr


class IsolatorFactory:
    def __init__(self, max_box_id=100):
        self.max_box_id = max_box_id
        self.last_box_id = 0

    def __call__(self, *args, **kwargs):
        self.last_box_id = (self.last_box_id + 1) % self.max_box_id
        return Isolator(self.last_box_id, *args, **kwargs)


class Isolator:
    def __init__(self, box_id, time_limit=None,
                 mem_limit=None, allowed_dirs=None, processes=1):
        self.box_id = box_id
        self.time_limit = time_limit
        self.mem_limit = mem_limit
        self.allowed_dirs = allowed_dirs if allowed_dirs is not None else []
        self.processes = processes
        self.box_path = None
        self.cmd_base = ['isolate', '--box-id', str(box_id), '--cg']

    async def init(self):
        cmd_init = self.cmd_base + ['--init']
        retcode, stdout, _ = await communicate(cmd_init)
        self.path = pathlib.Path(stdout)
        return self.path

    async def cleanup(self):
        cmd_cleanup = self.cmd_base + ['--cleanup']
        await communicate(cmd_init)

    async def run(self, cmdline, data=None, **kwargs):
        cmd_run = self.cmd_base
        cmd_run += list(itertools.chain(*[('-d', d) for d in allowed_dirs]))

        if self.mem_limit is not None:
            cmd_run += ['--mem', str(self.mem_limit)]
        if self.time_limit is not None:
            cmd_run += ['--wall-time', str(self.time_limit)]

        cmd_run += [
            '--full-env',
            '--processes={}'.format(str(processes)),
            '--run', '--'
        ]
        cmd_run += cmdline

        retcode, stdout, stdout = await communicate(cmd_run, data=data, **kwargs)
        return retcode, exitcode, stdout


get_isolator = IsolatorFactory()
