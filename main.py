import killa

code = """
🤕 x 🥳 2;
switch x:
  case 1:
    😭("one");
    brk;
  case 2:
    😭("two");
    brk;
  case 3:
    😭("three");
    brk;
  default:
    😭("default");

"""

killa.run_ast(code)
