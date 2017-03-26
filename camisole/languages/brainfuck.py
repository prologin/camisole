from camisole.languages.c import C
from camisole.models import Lang, PipelineLang, Program
from camisole.utils import which


class BrainfuckToC(Lang, register=False):
    source_ext = '.bf'
    extra_binaries = {'esotope': Program('esotope-bfc', version_opt=None)}
    compiler = Program('python2',
                       env={'PYTHONPATH': '/usr/lib/python2.7/site-packages'},
                       opts=['-S', extra_binaries['esotope'].cmd, '-v', '-fc'])

    def compile_opt_out(self, output):
        # there is no way to specify an output file, use stderr
        return []

    def read_compiled(self, path, isolator):
        return isolator.stdout.encode()


class Brainfuck(PipelineLang):
    source_ext = '.bf'
    sub_langs = [BrainfuckToC, C]
    reference_source = r'-[----->+<]>+.--.>++++++++++.'
