from collections import defaultdict
import subprocess
import sys

from camisole.languages import all, by_name, _import_builtins
_import_builtins()

# java packages consist of symlinks to handle both Java 7 & 8, so we force
# the version (8) here
OVERWRITE = {by_name('java'): {'/usr/lib/jvm/java-8-openjdk/bin/java',
                               '/usr/lib/jvm/java-8-openjdk/bin/javac'}}


def list_paths():
    for lang in all():
        cls = by_name(lang)
        if cls in OVERWRITE:
            for path in OVERWRITE[cls]:
                yield cls, path
            continue
        for p in cls.required_binaries():
            yield cls, p.cmd


def get_package(binary):
    try:
        return (subprocess.check_output(['pkgfile', '-qb', binary])
                .decode().split('\n')[0])
    except subprocess.CalledProcessError:
        pass


if __name__ == '__main__':
    lang_binaries = list_paths()
    packages = defaultdict(set)
    for lang, binary in lang_binaries:
        pkg = get_package(binary)
        if pkg is None:
            print("no package for", binary, file=sys.stderr)
            continue
        packages[pkg].add(lang)
    packages.pop('python')  # already a strong dependency
    packages = sorted(packages.items())
    lines = ["{:<20} # handle {} sources".format(
                "'{}'{}".format(pkg, ')' if i == len(packages) - 1 else ''),
                ', '.join(sorted(lang.__name__ for lang in langs)))
             for i, (pkg, langs) in enumerate(packages)]
    prefix = 'depends=('
    print('{}{}'.format(prefix, lines[0]))
    print('\n'.join(' ' * len(prefix) + line for line in lines[1:]))
