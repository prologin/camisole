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
import ctypes
import itertools
import logging
import os
import pathlib
import subprocess
import tempfile

from camisole.conf import conf
from camisole.utils import cached_classmethod


LIBC = ctypes.CDLL('libc.so.6')
LIBC.strsignal.restype = ctypes.c_char_p


def signal_message(signal: int) -> str:
    return LIBC.strsignal(signal).decode()


async def communicate(cmdline, data=None, **kwargs):
    logging.debug('Running %s', ' '.join(str(a) for a in cmdline))
    proc = await asyncio.create_subprocess_exec(
        *cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, **kwargs)
    stdout, stderr = await proc.communicate(data)
    retcode = await proc.wait()
    return retcode, stdout, stderr


CAMISOLE_OPTIONS = [
    'extra-time',
    'fsize',
    'mem',
    'processes',
    'quota',
    'stack',
    'time',
    'virt-mem',
    'wall-time',
]

CAMISOLE_TO_ISOLATE_OPTS = {
    # Memory is resident, if you want address space it's virtual memory
    'virt-mem': 'mem',
    'mem': 'cg-mem',
}

ISOLATE_TO_CAMISOLE_META = {
    # Consistency with the limit name
    # https://github.com/ioi/isolate/issues/20
    'time-wall': 'wall-time',
}


class IsolateInternalError(RuntimeError):
    def __init__(
        self,
        command,
        isolate_stdout,
        isolate_stderr,
        message="Isolate encountered an internal error."
    ):
        self.command = command
        self.isolate_stdout = isolate_stdout.decode(errors='replace').strip()
        self.isolate_stderr = isolate_stderr.decode(errors='replace').strip()

        message_list = [message]
        if self.isolate_stdout:
            message_list.append("Isolate output:\n    " + self.isolate_stdout)
        if self.isolate_stderr:
            message_list.append("Isolate error:\n    " + self.isolate_stderr)
        message_list.append("Command:\n    " + ' '.join(self.command))

        super().__init__('\n\n'.join(message_list))


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
            'cg-oom-killed': 0,
            'csw-forced': 0,
            'csw-voluntary': 0,
            'exitcode': 0,
            'exitsig': 0,
            'exitsig-message': None,
            'killed': False,
            'max-rss': 0,
            'message': None,
            'status': 'OK',
            'time': 0.0,
            'time-wall': 0.0,
        }
        with open(self.meta_file.name) as f:
            m = (line.strip() for line in f.readlines())
        m = dict(line.split(':', 1) for line in m if line)
        m = {k: (type(meta_defaults[k])(v)
                 if meta_defaults[k] is not None else v)
             for k, v in m.items()}
        if 'exitsig' in m:
            m['exitsig-message'] = signal_message(m['exitsig'])
        self.meta = {**meta_defaults, **m}
        verbose_status = {
            'OK': 'OK',
            'RE': 'RUNTIME_ERROR',
            'TO': 'TIMED_OUT',
            'SG': 'SIGNALED',
            'XX': 'INTERNAL_ERROR',
        }
        self.meta['status'] = verbose_status[self.meta['status']]

        if self.meta.get('cg-oom-killed'):
            self.meta['status'] = 'OUT_OF_MEMORY'

        for imeta, cmeta in ISOLATE_TO_CAMISOLE_META.items():
            if imeta in self.meta:
                self.meta[cmeta] = self.meta.pop(imeta)

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

        for opt in CAMISOLE_OPTIONS:
            v = self.opts.get(opt)
            iopt = CAMISOLE_TO_ISOLATE_OPTS.get(opt, opt)

            if v is not None:
                cmd_run.append(f'--{iopt}={v!s}')
            # Unlike isolate, we don't limit the number of processes by default
            elif iopt == 'processes':
                cmd_run.append('-p')

        for e in ['PATH', 'LD_LIBRARY_PATH', 'LANG']:
            env_value = os.getenv(e)
            if env_value:
                cmd_run += ['--env', e + '=' + env_value]

        for key, value in (env or {}).items():
            cmd_run += ['--env={}={}'.format(key, value)]

        cmd_run += [
            '--meta={}'.format(self.meta_file.name),
            '--stdout={}'.format(self.stdout_file),
        ]

        if merge_outputs:
            cmd_run.append('--stderr-to-stdout')
        else:
            cmd_run.append('--stderr={}'.format(self.stderr_file))

        cmd_run += ['--run', '--']
        cmd_run += cmdline

        self.isolate_retcode, self.isolate_stdout, self.isolate_stderr = (
            await communicate(cmd_run, data=data, **kwargs))

        self.stdout = b''
        self.stderr = b''
        if self.isolate_retcode >= 2:  # Internal error
            raise IsolateInternalError(
                cmd_run,
                self.isolate_stdout,
                self.isolate_stderr
            )
        try:
            self.stdout = (self.path / self.stdout_file).read_bytes()
            if not merge_outputs:
                self.stderr = (self.path / self.stderr_file).read_bytes()
        except (IOError, PermissionError) as e:
            # Something went wrong, isolate was killed before changing the
            # permissions or unreadable stdout/stderr
            raise IsolateInternalError(
                cmd_run,
                self.isolate_stdout,
                self.isolate_stderr,
                message="Error while reading stdout/stderr: " + e.message,
            )

    @cached_classmethod
    def isolate_conf(cls):
        parser = configparser.ConfigParser()
        s = 'dummy'

        def dummy_section():
            yield f'[{s}]'
            with pathlib.Path(conf['isolate-conf']).expanduser().open() as f:
                yield from f

        parser.read_file(dummy_section())
        root = pathlib.Path(parser.get(s, 'box_root'))
        max_boxes = parser.getint(s, 'num_boxes')
        return (collections.namedtuple('conf', 'root, max_boxes')
                (root, max_boxes))
