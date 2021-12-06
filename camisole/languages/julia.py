from camisole.models import Lang, Program


class Julia(Lang):
    source_ext = '.jl'
    interpreter = Program('julia')
    reference_source = 'print("42")'
