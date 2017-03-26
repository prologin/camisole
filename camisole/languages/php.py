from camisole.models import Lang, Program


class PHP(Lang):
    source_ext = '.php'
    interpreter = Program('php')
    reference_source = r'<?php echo "42\n";'
