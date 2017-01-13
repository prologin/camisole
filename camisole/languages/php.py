from camisole.models import Lang


class PHP(Lang):
    source_ext = '.php'
    interpreter = '/usr/bin/php'
    reference_source = r'<?php echo "42\n";'
