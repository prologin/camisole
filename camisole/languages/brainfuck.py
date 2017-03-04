from camisole.languages.c import C
from camisole.models import Lang, PipelineLang


class BrainfuckToC(Lang, register=False):
    _estope = 'esotope-bfc'
    source_ext = '.bf'
    compiler = 'python2'
    compile_opts = ['-S', _estope, '-v', '-fc']
    compile_env = {'PYTHONPATH': '/usr/lib/python2.7/site-packages'}
    extra_binaries = {_estope}

    def compile_opt_out(self, output):
        # there is no way to specify an output file, use stderr
        return []

    def read_compiled(self, path, isolator):
        return isolator.stdout.encode()


class Brainfuck(PipelineLang):
    source_ext = '.bf'
    sub_langs = [BrainfuckToC, C]
    reference_source = r'-[----->+<]>+.--.>++++++++++.'
