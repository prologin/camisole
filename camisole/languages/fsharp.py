from camisole.models import Lang, Program


class FSharp(Lang, name="F#"):
    source_ext = '.fs'
    compiler = Program('fsharpc', opts=['-O'], version_opt='--help')
    interpreter = Program('mono')
    reference_source = r'''
#light
open System
let () =
    Printf.printf "42\n"
'''
