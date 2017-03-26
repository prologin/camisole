from camisole.models import Lang, Program


class Lua(Lang):
    source_ext = '.lua'
    interpreter = Program('luajit', version_opt='-v')
    reference_source = r'print("42")'
