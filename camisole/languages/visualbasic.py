from camisole.models import Lang, Program


class VisualBasic(Lang):
    source_ext = '.vb'
    compiler = Program('vbnc', opts=['/optimize+'], version_opt='/help')
    interpreter = Program('mono')
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
