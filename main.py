import killa

code = """
var sum = 0;
for i in range(1, 6):  # i 從 1 到 5
    sum = sum + i;
prt(sum);  # 印出 15 (1+2+3+4+5)
"""

killa.run(code)