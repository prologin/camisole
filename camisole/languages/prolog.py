from camisole.models import Lang, Program


class Prolog(Lang):
    source_ext = '.pl'
    interpreter = Program('swipl',
                          opts=['--quiet', '-t', 'halt'],
                          version_opt='--version')
    reference_source = r":- write('42\n')."
