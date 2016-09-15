from camisole.models import Lang

class C(Lang):
    source_ext = '.c'
    compiler = '/usr/bin/gcc'
    compile_opts = ['-std=c11', '-Wall', '-Wextra', '-O2']


class CXX(Lang):
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

    def compile_opt_out(output):
        return ['-o' + output]


class Java(Lang):
    source_ext = '.java'
    compiler = '/usr/bin/javac'
    # TODO: weird class renaming


class CSharp(Lang):
    source_ext = '.cs'
    compiler = '/usr/bin/mcs'
    compile_opts = ['-optimize+']
    interpreter = '/usr/bin/mono'

    def compile_opt_out(output):
        return ['-out:' + output]


class FSharp(Lang):
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

    def compile_opt_out(output):
        return ['/out:' + output]


class Php(Lang):
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


class Brainfuck(Lang):
    # Todo: this one requires two compilers (bf and C++), no idea how to do
    # that cleanly.
    pass


languages = {cls.__name__.lower(): cls for cls in Lang.__subclasses__()}
