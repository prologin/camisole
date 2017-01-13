from camisole.models import Lang


class Javascript(Lang):
    source_ext = '.js'
    interpreter = '/usr/bin/node'
    reference_source = r"process.stdout.write('42\n');"
