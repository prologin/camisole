from camisole.models import Lang, Program


class CSharp(Lang, name="C#"):
    source_ext = '.cs'
    compiler = Program('mcs', opts=['-optimize+'])
    interpreter = Program('mono')
    reference_source = r'''
using System;
class Program
{
    public static void Main()
    {
        Console.WriteLine(42);
    }
}
'''

    def compile_opt_out(self, output):
        return ['-out:' + output]
