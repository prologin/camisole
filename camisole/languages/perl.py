from camisole.models import Lang


class Perl(Lang):
    source_ext = '.pl'
    interpreter = 'perl'
    reference_source = r'print "42\n";'
