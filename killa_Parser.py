import ply.yacc as yacc
from killa_Lexer import Lexer

variables = {}


# ----------- 表達式 -----------
def p_statement_expr(p):
    'statement : expression'
    val = p[1]

    def stmt():
        return val

    p[0] = stmt


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


def p_expression_var(p):
    'expression : ID'
    p[0] = variables.get(p[1], 0)

def evaluate_expression(expr):
    if callable(expr):
        return expr()
    return expr

# 支援變數再賦值（例如 x = x - 1）
def p_statement_reassign(p):
    'statement : ID EQUAL expression'
    varname = p[1]
    expr = p[3]

    def stmt():
        if callable(expr):
            variables[varname] = expr()
        else:
            variables[varname] = expr
        return variables[varname]

    p[0] = stmt


def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVISION expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression EQUAL_EQUAL expression
                  | expression NOTEQUAL expression'''
    left = p[1]
    right = p[3]

    def expr():
        # Evaluate operands if they're callable
        l_val = left() if callable(left) else left
        r_val = right() if callable(right) else right
        if p[2] == '+':
            return l_val + r_val
        elif p[2] == '-':
            return l_val - r_val
        elif p[2] == '*':
            return l_val * r_val
        elif p[2] == '/':
            return l_val / r_val
        elif p[2] == '<':
            return l_val < r_val
        elif p[2] == '<=':
            return l_val <= r_val
        elif p[2] == '>':
            return l_val > r_val
        elif p[2] == '>=':
            return l_val >= r_val
        elif p[2] == '==':
            return l_val == r_val
        elif p[2] == '!=':
            return l_val != r_val
        return None

    p[0] = expr


def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


# ----------- 賦值 -----------
def p_statement_assign(p):
    'statement : VAR ID EQUAL expression'
    val = p[4]
    def stmt():
        variables[p[2]] = val
        return val
    p[0] = stmt


# ----------- print -----------
def p_statement_prt(p):
    'statement : PRINT LPAREN expression RPAREN'
    val = p[3]

    def stmt():
        return val

    p[0] = stmt


# ----------- while -----------
# 在 while 中執行語句區塊（tuple 的每一個）
def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN statement'
    def loop():
        while evaluate_expression(p[3]):  # Evaluate condition each time
            if isinstance(p[5], tuple):
                for stmt in p[5]:
                    stmt()
            else:
                p[5]()  # Execute the body
        return None  # Return None when loop completes
    p[0] = loop



# 支援分號（;）語句分隔符號
def p_statement_semi(p):
    'statement : statement SEMI statement'
    stmt1 = p[1]
    stmt2 = p[3]

    def combined():
        stmt1()
        stmt2()

    p[0] = combined


# ----------- if-else -----------
def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN statement ELSE statement'
    cond = p[3]
    true_stmt = p[5]
    false_stmt = p[7]

    def stmt():
        if cond:
            true_stmt()
        else:
            false_stmt()

    p[0] = stmt


# ----------- statement group -----------
def p_statement_group(p):
    'statement : statement COLON statement'
    p[0] = p[3]  # 執行語意由左右兩側依序處理


# ----------- IN 表達式 -----------
def p_expression_in(p):
    'expression : expression IN LPAREN expression RPAREN'
    p[0] = p[1] in p[4]


# ----------- 錯誤處理 -----------
def p_error(p):
    print("Syntax Error" + str(p))


# 建立 parser
lexer = Lexer()
tokens = lexer.tokens
parser = yacc.yacc(start='statement')

# 讀取輸入
if __name__ == "__main__":
    while True:
        try:
            text = input('killa_input> ')
            if not text:
                continue
        except EOFError:
            break
        result = parser.parse(text, lexer=lexer.lexer)
        if result is not None:
            if callable(result):
                result = result()
            print(result)
