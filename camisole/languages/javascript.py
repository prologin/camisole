from camisole.models import Lang, Program


class Javascript(Lang):
    source_ext = '.js'
    interpreter = Program('node')
    reference_source = r"process.stdout.write('42\n');"
