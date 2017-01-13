from camisole.models import Lang


class C(Lang):
    source_ext = '.c'
    compiler = '/usr/bin/gcc'
    compile_opts = ['-std=c11', '-Wall', '-Wextra', '-O2']
    reference_source = r'''
#include <stdio.h>

int main(void)
{
    printf("42\n");
    return 0;
}
'''
