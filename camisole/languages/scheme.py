from camisole.models import Lang


class Scheme(Lang):
    source_ext = '.scm'
    interpreter = '/usr/bin/gsi'
    reference_source = r'(display "42")(newline)'
