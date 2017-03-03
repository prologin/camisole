from camisole.models import Lang


class Ruby(Lang):
    source_ext = '.rb'
    interpreter = '/usr/bin/ruby'
    reference_source = r'puts "42"'
