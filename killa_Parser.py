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


def evaluate_operand(operand):
    if callable(operand):
        result = operand()
        while callable(result):
            result = result()
        return result
    return operand


def p_expression_binop(p):
    '''expression : expression PLUSPLUS
                  | expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVISION expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression EQUAL_EQUAL expression
                  | expression NOTEQUAL expression
                  | expression DIVISIBILITY expression
                  '''
    if len(p) == 3:  # For unary operators like PLUSPLUS
        left = p[1]

        def expr():
            l_val = evaluate_operand(left)
            if p[2] == '++':
                return l_val + 1
            return None

        p[0] = expr()
    else:  # For binary operators
        left = p[1]
        right = p[3]

        def expr():
            l_val = evaluate_operand(left)
            r_val = evaluate_operand(right)

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

        p[0] = expr()


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

    p[0] = stmt()


# ----------- print -----------
def p_statement_prt(p):
    'statement : PRINT LPAREN expression RPAREN'
    val = p[3]

    def stmt():
        return val

    p[0] = stmt()


# ----------- while -----------
# 在 while 中執行語句區塊（tuple 的每一個）
def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN block'
    expr = p[3]
    block = p[5]

    def stmt():
        result = None
        while True:
            # Evaluate the condition
            condition = evaluate_expression(expr)
            if not condition:  # Break if condition is false
                break
                
            # Execute the block
            if callable(block):
                result = block()
            else:
                result = block
        return result

    p[0] = stmt()


def p_block_single(p):
    'block : statement'
    p[0] = p[1]


def p_block_multiple(p):
    'block : statement SEMI statement'
    stmt1 = p[1]
    stmt2 = p[3]

    def combined():
        val1 = stmt1() if callable(stmt1) else stmt1
        val2 = stmt2() if callable(stmt2) else stmt2
        return val2  # Return the last value

    p[0] = combined()


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
    """statement : IF LPAREN expression RPAREN block
                | IF LPAREN expression RPAREN block ELSE block"""
    if len(p) == 6:  # if without else
        cond = p[3]
        true_stmt = p[5]

        def stmt():
            if evaluate_expression(cond):
                return true_stmt() if callable(true_stmt) else true_stmt()
            return None

        p[0] = stmt
    else:  # if with else
        cond = p[3]
        true_stmt = p[5]
        false_stmt = p[7]

        def stmt():
            if evaluate_expression(cond):
                return true_stmt() if callable(true_stmt) else true_stmt()
            else:
                return false_stmt() if callable(false_stmt) else false_stmt()

        p[0] = stmt()


# ----------- IN 表達式 -----------
def p_expression_in(p):
    'expression : expression IN LPAREN expression RPAREN'
    p[0] = p[1] in p[4]


def p_expression_range(p):
    'expression : expression COLON expression'
    # 處理範圍
    start = p[1]
    end = p[3]
    p[0] = range(start, end)  # 返回一個範圍


# ----------- 錯誤處理 -----------
def p_error(p):
    print("Syntax Error" + str(p))


# 建立 parser
lexer = Lexer()
tokens = lexer.tokens
parser = yacc.yacc(start='statement', debug=False)

precedence = (
    ('right', 'EQUAL'),  # Assignment has lowest precedence
    ('left', 'SEMI'),  # Statement separator
    ('left', 'COLON'),  # Block separator
    ('left', 'ELSE'),  # Handle if-else
    ('left', 'EQUAL_EQUAL', 'NOTEQUAL'),  # Comparison operators
    ('left', 'LT', 'LE', 'GT', 'GE'),  # Relational operators
    ('left', 'PLUS', 'MINUS'),  # Addition and subtraction
    ('left', 'TIMES', 'DIVISION'),  # Multiplication and division
    ('right', 'PLUSPLUS'),  # Unary operators
    ('left', 'LPAREN', 'RPAREN'),  # Parentheses
)

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