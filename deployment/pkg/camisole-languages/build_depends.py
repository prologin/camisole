import subprocess
import sys
from pathlib import Path
from collections import defaultdict

from camisole.languages import Lang, load_builtins

load_builtins()


def by_name(name):
    return Lang._full_registry[name]


# AUR has no pkgfile mechanism; we provide a manually maintained list of
# binary -> package instead
AUR_PROVIDES = {'vbnc': 'mono-basic',
                'fsharpc': 'fsharp',
                'esotope-bfc': 'esotope-bfc-git'}

# java packages consist of symlinks to handle both Java 7 & 8, so we force
# the version (8) here
OVERWRITE = {by_name('java'): {'/usr/lib/jvm/java-8-openjdk/bin/java',
                               '/usr/lib/jvm/java-8-openjdk/bin/javac'}}


def error(msg):
    print("ERROR: " + msg, file=sys.stderr)


def list_paths():
    for lang in Lang._full_registry:
        cls = by_name(lang)
        if cls in OVERWRITE:
            for path in OVERWRITE[cls]:
                yield cls, Path(path)
            continue
        for p in cls.required_binaries():
            yield cls, Path(p.cmd)


def check_pkg_provides(pkg, name):
    try:
        contents = subprocess.check_output(['pacman', '-Qql', pkg])
    except subprocess.CalledProcessError:
        error(f"AUR package {pkg} not installed, cannot check contents")
        return False
    for line in contents.decode().splitlines():
        if Path(line.strip()).name == name:
            return True
    return False


def get_package(binary):
    pkg = None
    try:
        pkg = (subprocess.check_output(['pkgfile', '-qb', binary])
               .decode().split('\n')[0]) or None
    except subprocess.CalledProcessError:
        pass
    if pkg:
        return pkg
    if not pkg:
        pkg = AUR_PROVIDES.get(binary.name)
        if pkg and check_pkg_provides(pkg, binary.name):
            return pkg


if __name__ == '__main__':
    packages = defaultdict(set)
    for lang, binary in list_paths():
        pkg = get_package(binary)
        if pkg is None:
            error(f"no package for {binary}")
            continue
        packages[pkg].add(lang)
    packages.pop('python', None)  # already a strong dependency
    packages = sorted(packages.items())
    lines = ["{:<20} # handle {} sources".format(
        "'{}'{}".format(pkg, ')' if i == len(packages) - 1 else ''),
        ', '.join(sorted(lang.name for lang in langs)))
        for i, (pkg, langs) in enumerate(packages)]
    prefix = 'depends=('
    print('{}{}'.format(prefix, lines[0]))
    print('\n'.join(' ' * len(prefix) + line for line in lines[1:]))
