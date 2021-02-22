from camisole.models import Lang, Program

class LLVMAsm(Lang):
    source_ext = '.ll'
    compiler = Program('clang-8')
    interpreter = Program('lli-8')
    reference_source = r"""
@str42 = internal constant [4 x i8] c"42\0A\00"

declare i32 @printf(i8*, ...)

define i32 @main(...) nounwind {
entry:
  %strptr = getelementptr [4 x i8], [4 x i8]* @str42, i32 0, i32 0
  call i32 (i8*, ...) @printf( i8* %strptr ) nounwind
  ret i32 0
}"""
