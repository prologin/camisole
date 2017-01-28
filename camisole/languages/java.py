import re
from pathlib import Path

from camisole.models import Lang

RE_CLASS_DEF = re.compile(r'class\s+([^\s\{<]+)')


class Java(Lang):
    source_ext = '.java'
    compiled_ext = '.class'
    compiler = '/usr/bin/javac'
    interpreter = '/usr/bin/java'
    # /usr/lib/jvm/java-8-openjdk/jre/lib/amd64/jvm.cfg links to
    # /etc/java-8-openjdk/amd64/jvm.cfg
    allowed_dirs = ['/etc/java-8-openjdk']
    reference_source = r'''
public class JavaReference {
    public static void main(String args[]) {
        System.out.println(42);
    }
}
'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Don't even try to cgroup the java process:
        # http://stackoverflow.com/questions/19910468
        # https://bugs.launchpad.net/ubuntu/+source/openjdk-7/+bug/1241926
        # https://bugs.openjdk.java.net/browse/JDK-8071445
        # http://bugs.java.com/view_bug.do?bug_id=8043516

        # Instead, pass the memory limit as the maximum heap size of the
        # runtime.
        try:
            self.heapsize = self.opts['execute'].pop('mem')
        except KeyError:
            self.heapsize = None

    def compile_opt_out(self, output):
        # javac has no output directive, file name is class name
        return []

    def source_filename(self):
        # best-effort parsing of the class <foo> directive, class name is
        # stored in self.java_class for later use
        source = self.opts.get('source', '')
        match = RE_CLASS_DEF.search(source)
        # arbitrary fallback so we just get an error later
        self.java_class = 'Main'
        if match:
            self.java_class = match.group(1)
        return self.java_class + self.source_ext

    def execute_filename(self):
        return self.java_class + self.compiled_ext

    def execute_command(self, output):
        cmd = [self.interpreter]

        # Use the memory limit as a maximum heap size
        if self.heapsize is not None:
            cmd.append(f'-Xmx{self.heapsize}k')

        # foo/Bar.class is run with $ java -cp foo Bar
        cmd += ['-cp', str(Path(self.filter_box_prefix(output)).parent),
                self.java_class]
        return cmd
