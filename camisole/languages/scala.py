from camisole.languages.java import Java
from camisole.models import Program

class Scala(Java):
    source_ext = '.scala'
    compiled_ext = '.class'
    compiler = Program('scalac',opts=['-encoding', 'UTF-8'],env={'LANG': 'en_US.UTF-8'}, version_opt='-version')
    interpreter = Program('scala', version_opt='-version')
    reference_source = r'object Main extends App {println("42");}'
