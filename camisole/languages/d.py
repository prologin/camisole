from camisole.models import Lang, Program


class D(Lang):
    source_ext = '.d'
    compiler = Program('dmd')
    allowed_dirs = ['/etc']
    reference_source = r'''
void main()
{
    import std.stdio: writeln;
    writeln("42");
}
'''

    def compile_opt_out(self, output):
        # '-of' and its value as two distinct arguments is illegal (go figure)
        return ['-of' + output]
