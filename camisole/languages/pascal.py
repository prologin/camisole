from camisole.models import Lang


class Pascal(Lang):
    source_ext = '.pas'
    compiler = 'fpc'
    compile_opts = ['-XD', '-Fainitc']
    version_opt = '-h'
    version_lines = 1
    reference_source = r'''
program main;
begin
    Writeln(42);
end.
'''

    def compile_opt_out(self, output):
        return ['-o' + output]
