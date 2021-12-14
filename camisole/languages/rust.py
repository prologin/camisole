from camisole.models import Lang, Program


class Rust(Lang):
    source_ext = '.rs'
    compiler = Program('rustc', opts=['-W', 'warnings', '-C opt-level=3'])
    reference_source = r'fn main() { println!("42"); }'
