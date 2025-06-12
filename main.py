import killa

code = """
🤢 fib(n):
    if n <= 1:
        🍉 n;
    else:
        🍉 fib(n 😡 1) 🤌 fib(n 😡 2);
🥶

😭(fib(6));  # 預期輸出：8



"""

killa.run_ast(code)
