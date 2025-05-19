import ply.yacc as yacc
from killa_Lexer import Lexer

variables = {}


# ----------- 表達式 -----------
def p_statement_expr(p):
    'statement : expression'
    val = p[1]

    def stmt():
        if callable(val):
            return val()
        else:
            return val

    p[0] = stmt


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


def p_expression_var(p):
    'expression : ID'
    varname = p[1]

    def expr():
        return variables.get(varname, 0)

    p[0] = expr


def evaluate_expression(expr):
    if callable(expr):
        return expr()
    return expr


# ----------- 賦值 -----------
def p_statement_assign(p):
    'statement : VAR ID EQUAL expression SEMI'
    val = p[4]

    def stmt():
        variables[p[2]] = val
        return val

    p[0] = stmt


def evaluate_expression(expr):
    if callable(expr):
        result = expr()
        # Ensure we fully evaluate any nested callable results
        while callable(result):
            result = result()
        return result
    return expr


# 支援變數再賦值（例如 x = x - 1）
def p_statement_reassign(p):
    'statement : ID EQUAL expression SEMI'
    varname = p[1]
    expr = p[3]

    def stmt():
        val = expr() if callable(expr) else expr
        variables[varname] = val
        #print(f"DEBUG: {varname} = {variables[varname]}")
        return val

    p[0] = stmt


def evaluate_operand(operand):
    if callable(operand):
        result = operand()
        while callable(result):
            result = result()
        return result
    return operand


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
                  | expression NOTEQUAL expression
                  | expression DIVISIBILITY expression
                  '''
    left = p[1]
    right = p[3]
    op = p[2]

    def expr():
        l_val = left() if callable(left) else left
        r_val = right() if callable(right) else right
        if op == '+':
            return l_val + r_val
        elif op == '-':
            return l_val - r_val
        elif op == '*':
            return l_val * r_val
        elif op == '/':
            return l_val / r_val
        elif op == '<':
            return l_val < r_val
        elif op == '<=':
            return l_val <= r_val
        elif op == '>':
            return l_val > r_val
        elif op == '>=':
            return l_val >= r_val
        elif op == '==':
            return l_val == r_val
        elif op == '!=':
            return l_val != r_val
        elif op == '//':
            return l_val // r_val
        return None

    p[0] = expr  # <-- 這裡改成放函式本身，不是呼叫它


def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


# ----------- print -----------
def p_statement_prt(p):
    'statement : PRINT LPAREN expression RPAREN SEMI'
    val = p[3]

    def stmt():
        return val

    p[0] = stmt


# ----------- while -----------
# 在 while 中執行語句區塊（tuple 的每一個）
def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN COLON block'
    expr = p[3]
    block = p[6]

    def stmt():
        iteration = 0
        while evaluate_expression(expr):
            #print(f"While loop iteration {iteration}")
            iteration += 1
            if callable(block):
                result = block()
                if callable(result):
                    result()
        return result

    p[0] = stmt




def p_block_single(p):
    'block : statement'
    p[0] = p[1]


def p_block_pair(p):
    'block : block COLON statement'
    block = p[1]
    stmt = p[3]

    def combined():
        if callable(block):
            block()
        if callable(stmt):
            stmt()

    p[0] = combined


# 支援分號（;）語句分隔符號
def p_statement_semi(p):
    'statement : statement SEMI statement'
    stmt1 = p[1]
    stmt2 = p[3]

    def combined():
        if callable(stmt1):
            stmt1()
        if callable(stmt2):
            stmt2()

    p[0] = combined  # Note: don't call combined() here


def p_statement_list(p):
    '''statement_list : statement
                     | statement_list statement'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        stmt1 = p[1]
        stmt2 = p[2]

        def combined():
            if callable(stmt1):
                stmt1()
            if callable(stmt2):
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

        p[0] = stmt


# ----------- IN 表達式 -----------
def p_expression_in(p):
    'expression : expression IN LPAREN expression RPAREN'
    p[0] = p[1] in p[4]


# for 變數 in 範圍_start: _end:
def p_statement_for(p):
    'statement : FOR ID IN expression COLON expression COLON block'
    varname = p[2]
    start_expr = p[4]
    end_expr = p[6]
    body = p[8]

    def loop():
        start = evaluate_expression(start_expr)
        end = evaluate_expression(end_expr)
        for i in range(start, end):
            variables[varname] = i
            body()

    p[0] = loop


# ----------- 錯誤處理 -----------
def p_error(p):
    if p:
        print(f"Syntax Error at token {p}")
        # Print the token type and value
        print(f"Token type: {p.type}")
        print(f"Token value: {p.value}")
        print(f"Line number: {p.lineno}")
        print(f"Position: {p.lexpos}")
    else:
        print("Syntax Error at EOF")
    #breakpoint()


# Add this to help debug expression parsing
def p_expression_error(p):
    '''expression : error'''
    print(f"Expression error at {p}")
    #breakpoint()


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
