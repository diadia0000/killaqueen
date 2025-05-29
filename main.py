import killa

code = """
func hello():
    ret 100;
var x = hello();
prt(x);
"""

killa.run(code)