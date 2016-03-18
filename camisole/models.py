import subprocess

class Lang:
    source_ext = None
    compiler = None
    compile_opts = []
    interpreter = None
    interpret_opts = []
    version_opt = '--version'
    version_lines = None

    @staticmethod
    def compile_opt_out(out):
        return ['-o', out]

    @staticmethod
    def compile_command(inp, out):
        if compiler is None:
            return None
        return [compiler] + compile_opts + compile_opt_out(out) + [inp]

    @staticmethod
    def run_command(code):
        cmd = []
        if interpreter is not None:
            cmd += [interpreter] + interpret_opts
        return cmd + [code]
