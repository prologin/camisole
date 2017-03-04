from camisole.models import Lang


class Ruby(Lang):
    source_ext = '.rb'
    interpreter = 'ruby'
    reference_source = r'puts "42"'
