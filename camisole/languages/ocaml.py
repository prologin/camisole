from camisole.models import Lang


class OCaml(Lang):
    source_ext = '.ml'
    compiler = '/usr/bin/ocamlopt'
    compile_opts = ['-w', 'A']
    version_opt = '-v'
    version_lines = 1
    reference_source = r'print_int 42; print_string "\n";'
