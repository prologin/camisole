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

import functools
import os
import subprocess
import sys

from camisole.utils import parse_size, parse_float


def lscpu():
    out = subprocess.check_output('lscpu')
    out = out.decode().strip().split('\n')
    return {k: v.strip() for line in out for k, v in (line.split(':', 1),)}


def meminfo():
    with open('/proc/meminfo') as f:
        out = f.read().strip().split('\n')
    return {k: v.strip() for line in out for k, v in (line.split(':', 1),)}


# This function only gives static system information so we can cache it
# indefinitely.
@functools.lru_cache()
def info():
    uname = os.uname()
    cpu = lscpu()
    mem = meminfo()
    return {
        'arch': uname.machine,
        'byte_order': sys.byteorder,
        'cpu_cache_L1d': parse_size(cpu.get('L1d cache')),
        'cpu_cache_L1i': parse_size(cpu.get('L1i cache')),
        'cpu_cache_L2': parse_size(cpu.get('L2 cache')),
        'cpu_cache_L3': parse_size(cpu.get('L3 cache')),
        'cpu_count': os.cpu_count(),
        'cpu_mhz': parse_float(cpu.get('CPU MHz')),
        'cpu_name': cpu.get('Model name'),
        'kernel': uname.sysname,
        'kernel_release': uname.release,
        'kernel_version': uname.version,
        'memory': parse_size(mem.get('MemTotal'))
    }
