import re
from pathlib import Path

from camisole.models import Lang, PipelineLang


def all():
    return Lang._registry


def by_name(name):
    return all()[name.lower()]


class C(Lang):
    source_ext = '.c'
    compiler = '/usr/bin/gcc'
    compile_opts = ['-std=c11', '-Wall', '-Wextra', '-O2']


class CXX(Lang, name="C++"):
    source_ext = '.cc'
    compiler = '/usr/bin/g++'
    compile_opts = ['-std=c++11', '-Wall', '-Wextra', '-O2']


class Haskell(Lang):
    source_ext = '.hs'
    compiler = '/usr/bin/ghc'
    compile_opts = ['-dynamic', '-O2']


class OCaml(Lang):
    source_ext = '.ml'
    compiler = '/usr/bin/ocamlopt'
    compile_opts = ['-w', 'A']
    version_opt = '-v'
    version_lines = 1


class Ada(Lang):
    source_ext = '.adb'
    compiler = '/usr/bin/gnatmake'
    compile_opts = ['-f']


class Pascal(Lang):
    source_ext = '.pas'
    compiler = '/usr/bin/fpc'
    compile_opts = ['-XD', '-Fainitc']
    version_opt = '-h'
    version_lines = 1

    def compile_opt_out(self, output):
        return ['-o' + output]


class Java(Lang):
    source_ext = '.java'
    compiler = '/usr/bin/javac'
    # verbose, so that class names can be extracted from stderr
    compile_opts = ['-verbose']
    interpreter = '/usr/bin/java'
    # /usr/lib/jvm/java-8-openjdk/jre/lib/amd64/jvm.cfg links to
    # /etc/java-8-openjdk/amd64/jvm.cfg
    allowed_dirs = ['/etc/java-8-openjdk']

    def compile_opt_out(self, output):
        # javac has no output directive, file name is class name
        return []

    def read_compiled(self, path, isolator):
        # extract output class from javac stderr
        fname_reg = re.compile(r'^\[wrote RegularFileObject\[(.+?)\]\]$')
        for line in reversed(isolator.stderr.split('\n')):
            match = fname_reg.match(line)
            if match:
                wd = Path(isolator.path)
                fname = Path(match.group(1)).name
                # hack: store java class name in this instance
                self.java_class = Path(fname).stem
                return super().read_compiled(str(wd / fname), isolator)

    def execute_command(self, output):
        # foo/Bar.class is run with $ java -cp foo Bar
        return [self.interpreter,
                '-cp', str(Path(self.filter_box_prefix(output)).parent),
                self.java_class]

    def execute_filename(self):
        return self.java_class + '.class'


class CSharp(Lang, name="C#"):
    source_ext = '.cs'
    compiler = '/usr/bin/mcs'
    compile_opts = ['-optimize+']
    interpreter = '/usr/bin/mono'

    def compile_opt_out(self, output):
        return ['-out:' + output]


class FSharp(Lang, name="F#"):
    source_ext = '.fs'
    compiler = '/usr/bin/fsharpc'
    compile_opts = ['-O']
    version_lines = 4
    interpreter = '/usr/bin/mono'


class VisualBasic(Lang):
    source_ext = '.vb'
    compiler = '/usr/bin/vbnc'
    compile_opts = ['/optimize+']
    interpreter = '/usr/bin/mono'

    def compile_opt_out(self, output):
        return ['/out:' + output]


class PHP(Lang):
    source_ext = '.php'
    interpreter = '/usr/bin/php'


class Python(Lang):
    source_ext = '.py'
    interpreter = '/usr/bin/python3'
    interpret_opts = ['-S']


class Perl(Lang):
    source_ext = '.pl'
    interpreter = '/usr/bin/perl'


class Lua(Lang):
    source_ext = '.lua'
    interpreter = '/usr/bin/luajit'


class Scheme(Lang):
    source_ext = '.scm'
    interpreter = '/usr/bin/gsi'


class Javascript(Lang):
    source_ext = '.js'
    interpreter = '/usr/bin/node'


class BrainfuckToC(Lang, register=False):
    source_ext = '.bf'
    compiler = '/usr/bin/python2'
    compile_opts = ['-S', '/usr/bin/esotope-bfc', '-v', '-fc']
    compile_env = {'PYTHONPATH': '/usr/lib/python2.7/site-packages'}

    def compile_opt_out(self, output):
        # there is no way to specify an output file, use stderr
        return []

    def read_compiled(self, path, isolator):
        return isolator.stdout.encode()


class Brainfuck(PipelineLang):
    source_ext = '.bf'
    sub_langs = [BrainfuckToC, C]
