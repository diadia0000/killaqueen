import killa

code = """
🤕 i = 1;
🤕 sum = 0;

😺 i <= 5:
    sum = sum + i;
    i = i + 1;
    😭(sum);
"""

killa.run_ast(code)
