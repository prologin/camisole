from camisole.models import Lang, Program


class C(Lang):
    source_ext = '.c'
    compiler = Program('gcc',
                       opts=['-std=c11', '-Wall', '-Wextra', '-O2', '-lm'])
    reference_source = r'''
#include <stdio.h>

int main(void)
{
    printf("42\n");
    return 0;
}
'''
