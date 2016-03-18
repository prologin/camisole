from camisole.models import Lang

class C(Lang):
    source_ext = '.c'
    compiler = 'gcc'
    compile_opts = ['-std=c11', '-Wall', '-Wextra', '-O2']


class CXX(Lang):
    source_ext = '.cc'
    compiler = 'g++'
    compile_opts = ['-std=c++11', '-Wall', '-Wextra', '-O2']


class Haskell(Lang):
    source_ext = '.hs'
    compiler = 'ghc'
    compile_opts = ['-dynamic', '-O2']


class OCaml(Lang):
    source_ext = '.ml'
    compiler = 'ocamlopt'
    compile_opts = ['-w', 'A']
    version_opt = '-v'
    version_lines = 1


class Ada(Lang):
    source_ext = '.adb'
    compiler = 'gnatmake'
    compile_opts = ['-f']


class Pascal(Lang):
    source_ext = '.pas'
    compiler = 'fpc'
    compile_opts = ['-XD', '-Fainitc']
    version_opt = '-h'
    version_lines = 1

    def compile_opt_out(output):
        return ['-o' + output]


class Java(Lang):
    source_ext = '.java'
    compiler = 'javac'
    # TODO: weird class renaming


class CSharp(Lang):
    source_ext = '.cs'
    compiler = 'mcs'
    compile_opts = ['-optimize+']
    interpreter = 'mono'

    def compile_opts_out(output):
        return ['-out:' + output]


class FSharp(Lang):
    source_ext = '.fs'
    compiler = 'fsharpc'
    compile_opts = ['-O']
    version_lines = 4
    interpreter = 'mono'


class VisualBasic(Lang):
    source_ext = '.vb'
    compiler = 'vbnc'
    compile_opts = ['/optimize+']
    interpreter = 'mono'

    def compile_opts_out(output):
        return ['/out:' + output]


class Php(Lang):
    source_ext = '.php'
    interpreter = 'php'


class Python(Lang):
    source_ext = '.py'
    interpreter = 'python3'
    interpret_opts = ['-S']


class Perl(Lang):
    source_ext = '.pl'
    interpreter = 'perl'


class Lua(Lang):
    source_ext = '.lua'
    interpreter = 'luajit'


class Scheme(Lang):
    source_ext = '.scm'
    interpreter = 'gsi'


class Javascript(Lang):
    source_ext = '.js'
    interpreter = 'node'


class Brainfuck(Lang):
    # Todo: this one requires two compilers (bf and C++), no idea how to do
    # that cleanly.
    pass
