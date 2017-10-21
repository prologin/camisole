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
import collections
import configparser
import itertools
import logging
import pathlib
import subprocess
import tempfile

from camisole.conf import conf
from camisole.utils import cached_classmethod


async def communicate(cmdline, data=None, **kwargs):
    logging.debug('Running %s', ' '.join(cmdline))
    proc = await asyncio.create_subprocess_exec(
        *cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, **kwargs)
    stdout, stderr = await proc.communicate(data)
    retcode = await proc.wait()
    return retcode, stdout, stderr


OPTIONS = [
    'cg-mem',
    'extra-time',
    'fsize',
    'mem',
    'processes',
    'quota',
    'stack',
    'time',
    'wall-time',
]


class Isolator:
    def __init__(self, opts, allowed_dirs=None):
        self.opts = opts
        self.allowed_dirs = allowed_dirs if allowed_dirs is not None else []
        self.path = None
        self.cmd_base = None

        # Directory containing all the info of the program
        self.stdout_file = '._stdout'
        self.stderr_file = '._stderr'
        self.meta_file = None

        self.stdout = None
        self.stderr = None
        self.meta = None
        self.info = None

        # Result of the isolate binary
        self.isolate_retcode = None
        self.isolate_stdout = None
        self.isolate_stderr = None

    async def __aenter__(self):
        busy = {int(p.name) for p in self.isolate_conf.root.iterdir()}
        avail = set(range(self.isolate_conf.max_boxes)) - busy
        while avail:
            self.box_id = avail.pop()
            self.cmd_base = ['isolate', '--box-id', str(self.box_id), '--cg']
            cmd_init = self.cmd_base + ['--init']
            retcode, stdout, stderr = await communicate(cmd_init)
            if retcode == 2 and b"already exists" in stderr:
                continue
            if retcode != 0:  # noqa
                raise RuntimeError("{} returned code {}: “{}”".format(
                    cmd_init, retcode, stderr))
            break
        else:
            raise RuntimeError("No isolate box ID available.")
        self.path = pathlib.Path(stdout.strip().decode()) / 'box'
        self.meta_file = tempfile.NamedTemporaryFile(prefix='camisole-meta-')
        self.meta_file.__enter__()
        return self

    async def __aexit__(self, exc, value, tb):
        meta_defaults = {
            'cg-mem': 0,
            'csw-forced': 0,
            'csw-voluntary': 0,
            'exitcode': 0,
            'exitsig': None,
            'killed': False,
            'max-rss': 0,
            'message': None,
            'status': 'OK',
            'time': 0.0,
            'time-wall': 0.0,
        }
        with open(self.meta_file.name) as f:
            m = (l.strip() for l in f.readlines())
        m = dict(l.split(':', 1) for l in m if l)
        m = {k: (type(meta_defaults[k])(v)
                 if meta_defaults[k] is not None else v)
             for k, v in m.items()}
        self.meta = {**meta_defaults, **m}
        verbose_status = {
            'OK': 'OK',
            'RE': 'RUNTIME_ERROR',
            'TO': 'TIMED_OUT',
            'SG': 'SIGNALED',
            'XX': 'INTERNAL_ERROR',
        }
        self.meta['status'] = verbose_status[self.meta['status']]

        self.info = {
            'stdout': self.stdout,
            'stderr': self.stderr,
            'exitcode': self.isolate_retcode,
            'meta': self.meta
        }

        cmd_cleanup = self.cmd_base + ['--cleanup']
        retcode, stdout, stderr = await communicate(cmd_cleanup)
        if retcode != 0:  # noqa
            raise RuntimeError("{} returned code {}: “{}”".format(
                cmd_cleanup, retcode, stderr))

        self.meta_file.__exit__(exc, value, tb)

    async def run(self, cmdline, data=None, env=None,
                  merge_outputs=False, **kwargs):
        cmd_run = self.cmd_base[:]
        cmd_run += list(itertools.chain(
            *[('-d', d) for d in self.allowed_dirs]))

        for opt in OPTIONS:
            v = self.opts.get(opt)
            if v is not None:
                cmd_run.append(f'--{opt}={v!s}')
            # Unlike isolate, we don't limit the number of processes by default
            elif opt == 'processes':
                cmd_run.append('-p')

        for e in ['PATH', 'LD_LIBRARY_PATH', 'LANG']:
            cmd_run += ['--env', e]

        for key, value in (env or {}).items():
            cmd_run += ['--env={}={}'.format(key, value)]

        cmd_run += [
            '--meta={}'.format(self.meta_file.name),
            '--stdout={}'.format(self.stdout_file),
        ]

        if not merge_outputs:
            cmd_run.append('--stderr={}'.format(self.stderr_file))

        cmd_run += ['--run', '--']
        cmd_run += cmdline

        self.isolate_retcode, self.isolate_stdout, self.isolate_stderr = (
            await communicate(cmd_run, data=data, **kwargs))

        self.stdout = b''
        self.stderr = b''
        try:
            with (self.path / self.stdout_file).open('rb') as f:
                self.stdout = f.read()
            if not merge_outputs:
                with (self.path / self.stderr_file).open('rb') as f:
                    self.stderr = f.read()
        except (IOError, PermissionError):  # noqa
            # Something went wrong, isolate was killed before changing the
            # permissions or unreadable stdout/stderr
            pass

    @cached_classmethod
    def isolate_conf(cls):
        parser = configparser.ConfigParser()
        s = 'dummy'

        def dummy_section():
            yield f'[{s}]'
            yield from pathlib.Path(conf['isolate-conf']).expanduser().open()

        parser.read_file(dummy_section())
        root = pathlib.Path(parser.get(s, 'box_root'))
        max_boxes = parser.getint(s, 'num_boxes')
        return (collections.namedtuple('conf', 'root, max_boxes')
                (root, max_boxes))
