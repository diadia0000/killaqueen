import ply.yacc as yacc
from .killa_Lexer import Lexer
import sys

variables = {}


def p_program(p):
    '''program : statement
               | program statement'''
    if len(p) == 2:
        stmt = p[1]

        def program():
            return stmt() if callable(stmt) else stmt

        p[0] = program
    else:
        prev_prog = p[1]
        stmt = p[2]

        def program():
            if callable(prev_prog):
                prev_prog()
            return stmt() if callable(stmt) else stmt

        p[0] = program


# ----------- 表達式 -----------
def p_statement_expr(p):
    'statement : expression'
    val = p[1]

    #print(f"DEBUG [STMT_EXPR]: Got expression value {val}")  # Debug print

    def stmt():
        try:
            if callable(val):
                result = val()
                #print(f"DEBUG [STMT_EXPR]: Called expression, got {result}")  # Debug print
                return result
            else:
                #print(f"DEBUG [STMT_EXPR]: Non-callable value {val}")  # Debug print
                return val
        except Exception as e:
            raise f"Error evaluating expression: {e}"

    p[0] = stmt


def p_expression_number(p):
    'expression : NUMBER'
    val = p[1]

    #print(f"DEBUG [NUMBER]: Creating number expression with value {val}")  # Debug print

    def expr():
        return val

    p[0] = expr  # Return a function that returns the value

def p_expression_string(p):
    "expression : STRING"
    p[0] = p[1]


def p_expression_var(p):
    'expression : ID'
    var_name = p[1]

    def expr():
        if var_name in variables:
            val = variables[var_name]
            #print(f"DEBUG [VAR] Retrieved value {val} for {var_name}")
            return val
        else:
            raise NameError(f"Variable '{var_name}' not declared")

    p[0] = expr


# ----------- 賦值 -----------
def p_statement_assign(p):
    'statement : VAR ID EQUAL expression SEMI'
    if len(p) != 6:
        return None

    expr = p[4]
    var_name = p[2]

    def stmt():
        try:
            #print(f"DEBUG [ASSIGN] Starting assignment for {var_name}")  # New debug
            #print(f"DEBUG [ASSIGN] Expression is {expr}")  # New debug
            val = expr() if callable(expr) else expr
            #print(f"DEBUG [ASSIGN] Evaluated value is {val}")  # New debug
            if var_name:
                variables[var_name] = val
                #print(f"DEBUG [ASSIGN] Variables after assignment: {variables}")  # New debug
            return val
        except Exception as e:
            print(f"Error in assignment: {e}")
            return None

    p[0] = stmt


# 支援變數再賦值（例如 x = x - 1）
def p_statement_reassign(p):
    'statement : ID EQUAL expression SEMI'
    var_name = p[1]
    expr = p[3]

    def stmt():
        val = expr() if callable(expr) else expr
        if var_name in variables:
            variables[var_name] = val
            #print(f"DEBUG [REASSIGN] {var_name} updated to {val}")
        else:
            #print(f"WARNING: Variable '{var_name}' not declared, auto-declaring.")
            variables[var_name] = val
        return val

    p[0] = stmt


def evaluate_expression(expr):
    if isinstance(expr, tuple) and len(expr) == 3:
        left = evaluate_expression(expr[0])
        op = expr[1]
        right = evaluate_expression(expr[2])

        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
    if callable(expr):
        return expr()
    return expr


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
        if op == '/':
            if r_val == 0:
                raise ZeroDivisionError("Division by zero")
            result = l_val / r_val
        elif op == '-':
            result = l_val - r_val
        elif op == '+':
            result = l_val + r_val
        elif op == '*':
            result = l_val * r_val
        elif op == '>':
            result = l_val > r_val
        elif op == '<':
            result = l_val < r_val
        elif op == '>=':
            result = l_val >= r_val
        elif op == '<=':
            result = l_val <= r_val
        elif op == '==':
            result = l_val == r_val
        elif op == '!=':
            result = l_val != r_val
        else:
            raise RuntimeError(f"Unknown operator {op}")
        #print(f"DEBUG [BINOP]: {l_val} {op} {r_val} = {result}")
        return result

    p[0] = expr


def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


# ----------- print -----------
def p_statement_print(p):
    'statement : PRINT LPAREN expression RPAREN SEMI'
    expr = p[3]

    def stmt():
        val = evaluate_expression(expr)
        #print(f"DEBUG [PRINT]: About to print value {val}")
        print(val)
        return val

    p[0] = stmt


# ----------- while -----------
# 在 while 中執行語句區塊（tuple 的每一個）
def p_statement_while(p):
    'statement : WHILE LPAREN expression RPAREN COLON statements'
    expr = p[3]
    block = p[6]

    def stmt():
        iteration = 0
        while True:
            cond_val = evaluate_expression(expr)
            #print(f"DEBUG [WHILE] iteration {iteration}, condition value: {cond_val}")
            if not cond_val:
                break
            evaluate_expression(block)
            iteration += 1

    p[0] = stmt


def p_statements_single(p):
    'statements : statement'
    p[0] = p[1]


def p_statements_seq(p):
    'statements : statements statement'
    prev = p[1]
    stmt = p[2]

    def exec_block():
        evaluate_expression(prev)
        return evaluate_expression(stmt)

    p[0] = exec_block


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


# ----------- if-else -----------
def p_statement_if(p):
    """statement : IF expression COLON statements
                 | IF expression COLON statements ELSE COLON statements"""
    if len(p) == 5:
        cond = p[2]
        true_stmt = p[4]

        def stmt():
            if evaluate_expression(cond):
                return true_stmt() if callable(true_stmt) else true_stmt()
            return None

        p[0] = stmt
    else:
        cond = p[2]
        true_stmt = p[4]
        false_stmt = p[7]

        def stmt():
            if evaluate_expression(cond):
                return true_stmt() if callable(true_stmt) else true_stmt()
            else:
                return false_stmt() if callable(false_stmt) else false_stmt()

        p[0] = stmt



# ----------- IN 表達式 -----------
def p_expression_in(p):
    left = p[1]
    container = p[4]

    def expr():
        l_val = left() if callable(left) else left
        c_val = container() if callable(container) else container
        result = l_val in c_val
        #print(f"DEBUG [IN]: {l_val} in {c_val} = {result}")
        return result

    p[0] = expr


# for 變數 in 範圍_start: _end:
def p_statement_for(p):
    'statement : FOR ID IN RANGE LPAREN expression DOT expression RPAREN COLON statement'
    varname = p[2]
    start_expr = p[6]
    end_expr = p[8]
    body = p[11]

    def loop():
        start = evaluate_expression(start_expr)
        end = evaluate_expression(end_expr)
        for i in range(start, end):
            variables[varname] = i
            evaluate_expression(body)
        return None

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
        breakpoint()
    return


# Add this to help debug expression parsing
def p_expression_error(p):
    '''expression : error'''
    print(f"Expression error at {p}")
    breakpoint()
    return


# ---- 執行入口 ----
def run(code: str):
    # print(f"DEBUG [RUN]: Executing code:\n{code}")
    lexer = Lexer().build()
    parser = yacc.yacc(start='program', module=sys.modules[__name__])

    # Parse all statements
    ast = parser.parse(code, lexer=lexer)
    # print(f"DEBUG [RUN]: Parser returned {ast}")

    # Execute the program
    if callable(ast):
        try:
            # Execute the main program function
            result = ast()
            # print(f"DEBUG [RUN]: Program executed, final result = {result}")
            return result
        except Exception as e:
            raise f"Runtime error: {e}"
    return ast


# Define precedence and associativity
precedence = (
    ('left', 'EQUAL_EQUAL', 'NOTEQUAL'),  # 比較運算子
    ('left', 'LT', 'LE', 'GT', 'GE'),  # 關係運算子
    ('left', 'PLUS', 'MINUS'),  # 加減
    ('left', 'TIMES', 'DIVISION'),  # 乘除
    ('right', 'EQUAL')  # 賦值運算子右結合，最低優先度
)

# 建立 parser
lexer = Lexer()
tokens = lexer.tokens
parser = yacc.yacc(start='program', debug=True)

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
