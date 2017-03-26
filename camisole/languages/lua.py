from camisole.models import Lang, Program


class Lua(Lang):
    source_ext = '.lua'
    interpreter = Program('luajit')
    reference_source = r'print("42")'
