from camisole.models import Lang


class Scheme(Lang):
    source_ext = '.scm'
    interpreter = 'gsi'
    reference_source = r'(display "42")(newline)'
