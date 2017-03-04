from camisole.models import Lang


class Lua(Lang):
    source_ext = '.lua'
    interpreter = 'luajit'
    reference_source = r'print("42")'
