import ply.yacc as yacc
from killa_Lexer import Lexer  # 你的 Lexer 應該要定義 `tokens`

lexer = Lexer()  # 初始化 Lexer
tokens = lexer.tokens  # 取得 tokens
variables = {}  # 用來存放變數的字典


# 表達式或賦值
def p_statement(p):
    '''statement : assignment
                | expression'''
    p[0] = p[1]


# 加法
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]


# 減法
def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


# 乘法
def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]


# 除法
def p_term_div(p):
    'term : term DIVISION factor'
    p[0] = p[1] / p[3]


def p_term_factor(p):
    'term : factor'
    p[0] = p[1]


# 數字
def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]


# 括號
def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


# 處理變數 ID
def p_factor_id(p):
    'factor : ID'
    p[0] = variables.get(p[1], 0)  # 取得變數值，若不存在則預設為 0


# 賦值語法
def p_assignment_assign(p):
    'assignment : VAR ID EQUAL expression'
    variables[p[1]] = p[3]
    p[0] = p[3]


# if-else statement
def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN statement ELSE statement'
    if p[3]:  # 如果條件為 True，執行 if 區塊
        p[0] = p[5]
    else:  # 否則執行 else 區塊
        p[0] = p[7]


# 整數除法
def p_term_divisibility(p):
    'term : term DIVISIBILITY factor'
    p[0] = p[1] // p[3]


def p_term_dot(p):
    'term : term dot factor'
    p[0] = p[1] + p[3]


def p_statement_print(p):
    'statement : PRINT LPAREN expression RPAREN'
    print(p[3])
    p[0] = p[3]


# Error code
def p_error(p):
    print(f"Syntax Error: {p.value}")


def p_assignment_error(p):
    'assignment : ID EQUAL expression'
    print("Syntax Error: Use 'var' to declare variables.")
    p[0] = None


# build Parser
parser = yacc.yacc()

# read input
if __name__ == "__main__":
    while True:
        try:
            text = input('killa_input> ')
            if not text:
                continue
        except EOFError:
            break

        result = parser.parse(text, lexer=lexer.lexer)  # 正確地傳入 text
        print(result)
