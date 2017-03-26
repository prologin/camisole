from camisole.models import Lang, Program


class Scheme(Lang):
    source_ext = '.scm'
    interpreter = Program('gsi')
    reference_source = r'(display "42")(newline)'
