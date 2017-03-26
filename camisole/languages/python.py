from camisole.models import Lang, Program


class Python(Lang):
    source_ext = '.py'
    interpreter = Program('python3', opts=['-S'])
    reference_source = r'print("42")'
