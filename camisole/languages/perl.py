from camisole.models import Lang, Program


class Perl(Lang):
    source_ext = '.pl'
    interpreter = Program('perl')
    reference_source = r'print "42\n";'
