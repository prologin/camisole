from camisole.models import Lang


class Ada(Lang):
    source_ext = '.adb'
    compiler = '/usr/bin/gnatmake'
    compile_opts = ['-f']
    reference_source = r'''
with Ada.Text_IO; use Ada.Text_IO;
procedure Hello is
begin
   Put_Line("42");
end Hello;
'''
