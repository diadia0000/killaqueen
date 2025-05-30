import killa

code = """
var sum = 0;
for i in range 0 5: 
    sum = sum + i;
prt sum;

"""

killa.run_ast(code)
