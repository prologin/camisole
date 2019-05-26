from camisole.models import Lang, Program


class Go(Lang):
    source_ext = '.go'
    compiler = Program('go', opts=['build', '-buildmode=exe'],
                       version_opt='version')
    reference_source = r'''
package main
import "fmt"
func main() {
    fmt.Println("42")
}
'''
