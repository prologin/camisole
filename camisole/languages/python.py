from camisole.models import Lang


class Python(Lang):
    source_ext = '.py'
    interpreter = '/usr/bin/python3'
    interpret_opts = ['-S']
    reference_source = r'print("42")'
