import ply.yacc as yacc
from killa_Lexer import Lexer  # 你的 Lexer 應該要定義 `tokens`

lexer = Lexer()  # 初始化 Lexer
tokens = lexer.tokens  # 取得 tokens
variables = {}  # 用來存放變數的字典


# 運算表達式
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]


def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


# 乘法 / 除法
def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]


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


# 處理變數 ID
def p_factor_id(p):
    'factor : ID'
    p[0] = variables.get(p[1], 0)  # 取得變數值，若不存在則預設為 0


# 括號運算
def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


# 賦值語句
def p_assignment_assign(p):
    'statement : ID EQUAL expression'
    variables[p[1]] = p[3]
    p[0] = p[3]


# 表達式或賦值
def p_statement_expr(p):
    'statement : expression'
    p[0] = p[1]


# 錯誤處理
def p_error(p):
    if p:
        print(f"Syntax Erro: {p.value}")
    else:
        print("語法錯誤！")

def p_factor_id(p):
    'factor : ID'
    p[0] = variables.get(p[1], 0)



# 建立 Parser
parser = yacc.yacc()

# 讀取使用者輸入
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