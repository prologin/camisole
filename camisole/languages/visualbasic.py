from camisole.models import Lang


class VisualBasic(Lang):
    source_ext = '.vb'
    compiler = '/usr/bin/vbnc'
    compile_opts = ['/optimize+']
    interpreter = '/usr/bin/mono'
    reference_source = r'''
Imports System
Public Module modmain
Sub Main()
    Console.WriteLine ("42")
End Sub
End Module
'''

    def compile_opt_out(self, output):
        return ['/out:' + output]
