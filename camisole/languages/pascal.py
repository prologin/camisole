from camisole.models import Lang, Program


class Pascal(Lang):
    source_ext = '.pas'
    compiler = Program('fpc', opts=['-XD', '-Fainitc'],
                       version_opt='-h', version_lines=1)
    reference_source = r'''
program main;
begin
    Writeln(42);
end.
'''

    def compile_opt_out(self, output):
        return ['-o' + output]
