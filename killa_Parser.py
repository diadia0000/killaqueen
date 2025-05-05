import ply.yacc as yacc
from killa_Lexer import Lexer

variables = {}


# ----------- 表達式 -----------
def p_expression_number(p):
    'expression : NUMBER'
    p[0] = lambda: p[1]


def p_expression_var(p):
    'expression : ID'
    p[0] = lambda: variables.get(p[1], 0)


def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVISION expression
                  | expression LT expression
                  | expression GT expression'''
    left = p[1]
    right = p[3]
    if p[2] == '+':
        p[0] = lambda: left() + right()
    elif p[2] == '-':
        p[0] = lambda: left() - right()
    elif p[2] == '*':
        p[0] = lambda: left() * right()
    elif p[2] == '/':
        p[0] = lambda: left() / right()
    elif p[2] == '<':
        p[0] = lambda: left() < right()
    elif p[2] == '>':
        p[0] = lambda: left() > right()


def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


# ----------- 賦值 -----------
def p_statement_assign(p):
    'statement : VAR ID EQUAL expression'
    expr = p[3]
    p[0] = lambda: variables.__setitem__(p[1], expr())


# ----------- print -----------
def p_statement_print(p):
    'statement : PRINT LPAREN expression RPAREN'
    expr = p[3]
    p[0] = lambda: print(expr())


# ----------- while -----------
def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN statement'
    cond = p[3]
    body = p[5]

    def loop():
        while cond():
            body()

    p[0] = loop


# ----------- if-else -----------
def p_statement_if(p):
    'statement : IF LPAREN expression RPAREN statement ELSE statement'
    cond = p[3]
    body_if = p[5]
    body_else = p[7]

    def branch():
        if cond():
            body_if()
        else:
            body_else()

    p[0] = branch


# ----------- statement block 或 單一 statement -----------
def p_statement_group(p):
    'statement : statement COLON statement'
    stmt = p[1]  # 冒號後是接著的語句
    p[0] = stmt


def p_statement_single(p):
    'statement : expression'
    expr = p[1]
    p[0] = lambda: expr()


def p_error(p):
    print('Syntax Error')


# 大於等於
def p_expression_ge(p):
    'expression : expression GE expression'
    p[0] = p[1] >= p[3]


# 小於等於
def p_expression_le(p):
    'expression : expression LE expression'
    p[0] = p[1] <= p[3]


# IN 用於檢查是否在範圍內
def p_expression_in(p):
    'expression : expression IN LPAREN expression RPAREN'
    p[0] = p[1] in p[4]  # 假設 p[4] 是一個列表或範圍


# build Parser
lexer = Lexer()
tokens = lexer.tokens
parser = yacc.yacc(start='statement')

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
