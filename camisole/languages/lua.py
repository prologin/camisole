from camisole.models import Lang


class Lua(Lang):
    source_ext = '.lua'
    interpreter = '/usr/bin/luajit'
    reference_source = r'print("42")'
