import re
import subprocess
from pathlib import Path

from camisole.models import Lang, Program

# In Java, the entry point (main() function) is not trivial to find as it can be
# defined as a method of any of the classes contained in the source program.
# Even though we could force Java users to respect a standard name for their
# class (eg. public class Main), we can do better by finding where the main()
# method is defined, however deep in the class tree.

# Quick explanation how the Java compile/execute workflow works:
# 1.  source is written in a file named 1337.java; '1337' cannot be used as a
#     class name (identifiers cannot start with a number) so this will trigger
#     the error explained in 3a.
# 2.  compile (javac) that 1337.java file
# 3a. if source contains a root *public* class, javac will complain that its
#     name is different than the .java filename (1337.java), hence:
#     4a. we look for the actual class name by parsing javac stderr output
#     5a. compile again with the new, actual class name as filename
# 3b. if there is no public class, javac will not complain but produce
#     one or multiple .class files (one per class and nested class), hence:
#     4b. we iterate over every *.class in the output directory, running javap
#         (disassembler) so as to find a main() signature
#     5b. we stop at the first valid main() signature and use the .class file
#         it belongs to as java (interpreter) target.

RE_WRONG_FILENAME_ERROR = re.compile(r'error:\s+class\s+(.+?)\s+is\s+public,')
PSVMAIN_DESCRIPTOR = 'descriptor: ([Ljava/lang/String;)V'


class Java(Lang):
    source_ext = '.java'
    compiled_ext = '.class'
    compiler = Program('javac', opts=['-encoding', 'UTF-8'],
                       env={'LANG': 'en_US.UTF-8'}, version_opt='-version')
    interpreter = Program('java', version_opt='-version')
    # /usr/lib/jvm/java-8-openjdk/jre/lib/amd64/jvm.cfg links to
    # /etc/java-8-openjdk/amd64/jvm.cfg
    allowed_dirs = ['/etc/java-8-openjdk']
    # ensure we can parse the javac(1) stderr
    extra_binaries = {'disassembler': Program('javap', version_opt='-version')}
    reference_source = '''
class MyπClass {
    static int fortytwo() {
        return 42;
    }
    static class Subclassé {
        public static void main(String notMe) {}
        final static public void main(String args[]) {
           System.out.println(MyπClass.fortytwo());
        }
    }
}
'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # use an illegal class name so that javac(1) will spit out the actual
        # class named used in the source
        self.class_name = '1337'
        # we give priority to the public class, if any, so keep a flag if we
        # found such a public class
        self.found_public = False

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

    async def compile(self):
        # try to compile with default class name (Main)
        retcode, info, binary = await super().compile()
        if retcode != 0:
            # error: public class name is not '1337' as it's an illegal name,
            # so find what it actually is
            try:
                javac_stderr = info['stderr'].decode()
            except UnicodeDecodeError:  # noqa
                raise RuntimeError(
                    "could not decode javac stderr to find class name")
            match = RE_WRONG_FILENAME_ERROR.search(javac_stderr)
            if match:
                self.found_public = True
                self.class_name = match.group(1)
                # retry with new name
                retcode, info, binary = await super().compile()
        return (retcode, info, binary)

    def source_filename(self):
        return self.class_name + self.source_ext

    def execute_filename(self):
        # return eg. Main.class
        return self.class_name + self.compiled_ext

    def execute_command(self, output):
        cmd = [self.interpreter.cmd] + self.interpreter.opts

        # Use the memory limit as a maximum heap size
        if self.heapsize is not None:
            cmd.append(f'-Xmx{self.heapsize}k')

        # foo/Bar.class is run with $ java -cp foo Bar
        cmd += ['-cp', str(Path(self.filter_box_prefix(output)).parent),
                self.class_name]
        return cmd

    def find_class_having_main(self, classes):
        for file in classes:
            # run javap(1) with type signatures
            try:
                stdout = subprocess.check_output(
                    [self.extra_binaries['disassembler'].cmd, '-s', str(file)],
                    stderr=subprocess.DEVNULL, env=self.compiler.env)
            except subprocess.SubprocessError:  # noqa
                continue
            # iterate on lines to find p s v main() signature and then
            # its descriptor on the line below; we don't rely on the type
            # from the signature, because it could be String[], String... or
            # some other syntax I'm not even aware of
            lines = iter(stdout.decode().split('\n'))
            for line in lines:
                line = line.lstrip()
                if line.startswith('public static') and 'void main(' in line:
                    if next(lines).lstrip() == PSVMAIN_DESCRIPTOR:
                        return file.stem

    def read_compiled(self, path, isolator):
        # in case of multiple or nested classes, multiple .class files are
        # generated by javac
        classes = list(isolator.path.glob('*.class'))
        files = [(file.name, file.open('rb').read()) for file in classes]
        if not self.found_public:
            # the main() may be anywhere, so run javap(1) on all .class
            new_class_name = self.find_class_having_main(classes)
            if new_class_name:
                self.class_name = new_class_name
        return files

    def write_binary(self, path, binary):
        # see read_compiled(), we need to write back all .class files
        # but give only the main class name (execute_filename()) to java(1)
        for file, data in binary:
            with (path / file).open('wb') as c:
                c.write(data)
        return path / self.execute_filename()
