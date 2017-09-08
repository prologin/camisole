from camisole.models import Lang, Program


class CompiledLang(Lang):
    compiler = Program('echo')


class InterpretedLang(Lang):
    interpreter = Program('echo')
