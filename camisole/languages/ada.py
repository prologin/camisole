from camisole.models import Lang, Program


class Ada(Lang):
    source_ext = '.adb'
    compiler = Program('gnatmake', opts=['-f'])
    reference_source = r'''
with Ada.Text_IO; use Ada.Text_IO;
procedure Hello is
begin
   Put_Line("42");
end Hello;
'''
