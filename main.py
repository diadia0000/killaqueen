import killa

code = """
var happy = 😀;
var sad = 😫;

if happy and not sad:
    prt 123;

"""

killa.run_ast(code)
