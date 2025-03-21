import ply.yacc
from ply.yacc import *
from killa_Lexer import Lexer

lexer = Lexer()
tokens = lexer.tokens


def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]


def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]


def p_term_div(p):
    'term : term DIVISION factor'
    p[0] = p[1] / p[3]


def p_term_factor(p):
    'term : factor'
    p[0] = p[1]


def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]


def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


# Build the parser
parser = ply.yacc.yacc()
if __name__ == "__main__":
    while True:
        try:
            s = input("Enter your counting")
            print(s)
        except EOFError:
            break
        if not s: continue
        result = parser.parse(lexer=lexer.lexer)
        print(result)
