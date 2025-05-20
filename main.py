import killa

code = """
func foo():
    ret 42;
var x = foo();
prt(x);
"""

killa.run(code)