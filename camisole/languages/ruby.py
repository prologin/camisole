from camisole.models import Lang, Program


class Ruby(Lang):
    source_ext = '.rb'
    interpreter = Program('ruby')
    reference_source = r'puts "42"'
