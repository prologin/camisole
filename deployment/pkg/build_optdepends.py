from collections import defaultdict
import subprocess
import sys

from camisole.languages import all, by_name, Brainfuck, FSharp

FROM_AUR = {'esotope-bfc-git': {Brainfuck},
            'fsharp': {FSharp}}


def list_paths():
    for lang in all():
        cls = by_name(lang)
        if cls.compiler:
            yield cls, cls.compiler
        if cls.interpreter:
            yield cls, cls.interpreter


def get_package(binary):
    try:
        return (subprocess.check_output(['pkgfile', '-qb', binary])
                .decode().split('\n')[0])
    except subprocess.CalledProcessError:
        pass


if __name__ == '__main__':
    lang_binaries = list_paths()
    packages = defaultdict(set)
    packages.update(FROM_AUR)
    for lang, binary in lang_binaries:
        pkg = get_package(binary)
        if pkg is None:
            print("no package for", binary, file=sys.stderr)
            continue
        packages[pkg].add(lang)
    packages.pop('python')  # already a strong dependency
    packages = sorted(packages.items())
    lines = ["'{}: compile {} sources'".format(pkg, ', '.join(sorted(lang.__name__ for lang in langs)))
             for pkg, langs in packages]
    prefix = 'optdepends=('
    print('{}{}'.format(prefix, lines[0]))
    print('\n'.join(' ' * len(prefix) + line for line in lines[1:]), end=')')
    print()
