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

        # FIXME: we need to specify a heap size that's way lower than the total
        # amount of memory allowed in the cgroup, so that Java is able to
        # allocate the heap, the stack and the runtime in this address space.
        try:
            # heap_constraint = max(32, (self.opts['execute']['mem'] - 400000) // 1024)
            heap_constraint = 128
            cmd += [f'-XX:MaxHeapSize={heap_constraint}M',
                    f'-XX:MaxMetaspaceSize=16M',
                    f'-XX:CompressedClassSpaceSize=4M',
                    f'-XX:ReservedCodeCacheSize=4M',
                    '-XX:+UseConcMarkSweepGC']

        except KeyError:
            pass

        # foo/Bar.class is run with $ java -cp foo Bar
        cmd += ['-cp', str(Path(self.filter_box_prefix(output)).parent),
                self.java_class]

        return cmd
