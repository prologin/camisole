import re
from pathlib import Path

from camisole.models import Lang


class Java(Lang):
    source_ext = '.java'
    compiler = '/usr/bin/javac'
    # verbose, so that class names can be extracted from stderr
    compile_opts = ['-verbose']
    interpreter = '/usr/bin/java'
    # /usr/lib/jvm/java-8-openjdk/jre/lib/amd64/jvm.cfg links to
    # /etc/java-8-openjdk/amd64/jvm.cfg
    allowed_dirs = ['/etc/java-8-openjdk']
    reference_source = r'''
class Main
{
    public static void main(String args[])
    {
        System.out.println(42);
    }
}
'''

    def compile_opt_out(self, output):
        # javac has no output directive, file name is class name
        return []

    def read_compiled(self, path, isolator):
        # extract output class from javac stderr
        fname_reg = re.compile(r'^\[wrote RegularFileObject\[(.+?)\]\]$')
        for line in reversed(isolator.stderr.split('\n')):
            match = fname_reg.match(line)
            if match:
                wd = Path(isolator.path)
                fname = Path(match.group(1)).name
                # hack: store java class name in this instance
                self.java_class = Path(fname).stem
                return super().read_compiled(str(wd / fname), isolator)

    def execute_command(self, output):
        # foo/Bar.class is run with $ java -cp foo Bar
        return [self.interpreter,
                '-cp', str(Path(self.filter_box_prefix(output)).parent),
                self.java_class]

    def execute_filename(self):
        return self.java_class + '.class'
