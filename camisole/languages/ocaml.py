from camisole.models import Lang, Program


class OCaml(Lang):
    source_ext = '.ml'
    compiler = Program('ocamlopt', opts=['-w', 'A'])
    reference_source = r'print_int 42; print_string "\n";'
