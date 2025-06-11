# killa_Parser.py — 改寫為 class-based 結構，使用 re-based Lexer

from .killa_Lexer import Lexer
from .killa_ast import *
from .error import KillaSyntaxError, KillaRuntimeError, KillaReturn


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class Function:
    def __init__(self, name, params, body_tokens, closure):
        self.name = name
        self.params = params
        self.body_tokens = body_tokens
        self.closure = closure  # the environment where the function was defined

    def call(self, interpreter, arguments):
        env = Environment(self.closure)
        for i in range(len(self.params)):
            env.define(self.params[i], arguments[i])

        old_env = interpreter.environment
        interpreter.environment = env

        try:
            for stmt in self.body_tokens:  # Now these are AST nodes
                interpreter.execute(stmt)
        except KillaReturn as r:
            interpreter.environment = old_env
            return r.value

        interpreter.environment = old_env
        return None


class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, value):
        if name in self.values:
            raise KillaRuntimeError(f"Variable '{name}' already declared in this scope.")
        self.values[name] = value

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise KillaRuntimeError(f"Undefined variable '{name}'.")

    def get(self, name):
        if name in self.values:
            return self.values[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise KillaRuntimeError(f"Undefined variable '{name}'.")

    def exists(self, name):
        if name in self.values:
            return True
        elif self.parent:
            return self.parent.exists(name)
        return False


class UnaryExpression(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class KillaInterpreter:
    def __init__(self):
        self._tokens = None
        self.environment = Environment()
        self.functions = {}
        self.lexer = Lexer()

    def evaluate(self, expr):
        if isinstance(expr, tuple) and len(expr) == 3:
            left = self.evaluate(expr[0])
            op = expr[1]
            right = self.evaluate(expr[2])
            return self.eval_op(left, op, right)
        if callable(expr):
            return expr()
        if isinstance(expr, str) and expr in self.environment:
            return self.environment.get(expr)
        return expr

    def eval_op(self, left, op, right):
        if op == '🤌': return left + right
        if op == '😡': return left - right
        if op == '☹️': return left * right
        if op == '🤬': return left / right
        if op == '//': return left // right
        if op == '>': return left > right
        if op == '<': return left < right
        if op == '>=': return left >= right
        if op == '<=': return left <= right
        if op == '==': return left == right
        if op == '!=': return left != right
        # Logical operators
        if op == 'and': return left and right
        if op == 'or': return left or right
        raise KillaRuntimeError(f"Unknown operator {op}")

    def eval_unary_op(self, op, operand):
        """Handle unary operators like 'not'"""
        if op == 'not':
            return not operand
        if op == '😡':
            return -operand
        if op == '🤌':
            return +operand
        raise KillaRuntimeError(f"Unknown unary operator {op}")

    def parse_and_run(self, code):
        # TEMP: original interpreter path
        self.lexer.input(code)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            # print(f"[TOKEN] {tok.type}: {tok.value}")

    def _handle_var_assign(self):
        id_token = self.lexer.token()
        eq_token = self.lexer.token()
        expr_token = self.lexer.token()
        semi_token = self.lexer.token()

        if id_token.type != 'ID' or eq_token.type != 'EQUAL' or semi_token.type != 'SEMI':
            raise KillaSyntaxError("Invalid variable assignment syntax")

        value = self._evaluate_literal(expr_token)
        self.environment.define(id_token.value, value)
        # print(f"[ASSIGN] var {id_token.value} = {value}")

    def _handle_reassign(self, id_token):
        eq_token = self.lexer.token()
        left_token = self.lexer.token()
        op_token = self.lexer.token()
        right_token = self.lexer.token()
        semi_token = self.lexer.token()

        if eq_token.type != 'EQUAL' or semi_token.type != 'SEMI':
            raise KillaSyntaxError("Invalid reassignment syntax")

        # Handle expressions like x = x + 1;
        if left_token and op_token and right_token:
            left_val = self._evaluate_literal(left_token)
            right_val = self._evaluate_literal(right_token)
            result = self.eval_op(left_val, op_token.value, right_val)
        else:
            result = self._evaluate_literal(left_token)

        self.environment.assign(id_token.value, result)
        # print(f"[REASSIGN] {id_token.value} = {result}")

    def _evaluate_literal(self, token):
        if token.type == 'NUMBER':
            return token.value
        elif token.type == 'STRING':
            return token.value
        elif token.type == 'ID':
            try:
                return self.environment.get(token.value)
            except RuntimeError:
                return 0  # fallback if variable is undefined
        else:
            raise KillaSyntaxError(f"Unsupported expression type: {token.type}")

    def _handle_print(self):
        expr_token = self.lexer.token()
        semi_token = self.lexer.token()

        if semi_token.type != 'SEMI':
            raise KillaSyntaxError("Missing semicolon after print")

        value = self._evaluate_literal(expr_token)
        print(value)

    def _handle_if(self):
        # Parse condition like: if x > 5:
        condition = self._parse_condition()

        colon_token = self.lexer.token()
        if colon_token.type != 'COLON':
            raise KillaSyntaxError("Missing ':' after if condition")

        if condition:
            self._run_next_statement()
            # Check if 'else' follow, and skip it
            next_tok = self.lexer.token()
            if next_tok and next_tok.type == 'ELSE':
                colon = self.lexer.token()
                if colon.type != 'COLON':
                    raise KillaSyntaxError("Missing ':' after else")
                self._skip_next_statement()
            elif next_tok:
                self.lexer._tokens.insert(0, next_tok)  # Not else? Put it back.
        else:
            # False condition, check for 'else'
            next_tok = self.lexer._token()
            if next_tok and next_tok.type == 'ELSE':
                self._handle_else()
            elif next_tok:
                self.lexer._tokens.insert(0, next_tok)

    def _handle_else(self):
        colon = self.lexer._token()
        if colon.type != 'COLON':
            raise KillaSyntaxError("Missing ':' after else")
        self._run_next_statement()

    def _skip_next_statement(self):
        # Consume one statement’s worth of tokens
        tok = self.lexer._token()
        if tok.type in ('VAR', 'PRINT', 'ID', 'IF'):
            # Consume next few tokens to simulate skipping
            for _ in range(3):  # crude skip (could be improved)
                if not self.lexer._token():
                    break
        else:
            raise KillaSyntaxError(f"Unexpected token while skipping: {tok.type}")

    def _parse_condition(self):
        left = self.lexer.token()
        op = self.lexer.token()
        right = self.lexer.token()

        if not (left and op and right):
            raise KillaSyntaxError("Incomplete condition")

        left_val = self._evaluate_literal(left)
        right_val = self._evaluate_literal(right)

        return self.eval_op(left_val, op.value, right_val)

    def _run_next_statement(self):
        tok = self.lexer.token()
        if tok.type == 'VAR':
            self._handle_var_assign()
        elif tok.type == 'ID':
            self._handle_reassign(tok)
        elif tok.type == 'PRINT':
            self._handle_print()
        elif tok.type == 'IF':
            self._handle_if()
        else:
            raise KillaSyntaxError(f"Unknown statement type in if/else: {tok.type}")

    def _handle_for(self):
        var_token = self.lexer.token()  # i
        in_token = self.lexer.token()
        range_token = self.lexer.token()
        start_token = self.lexer.token()
        end_token = self.lexer.token()
        colon_token = self.lexer.token()

        if not (var_token.type == 'ID' and in_token.type == 'IN' and
                range_token.type == 'RANGE' and colon_token.type == 'COLON'):
            raise KillaSyntaxError("Invalid for loop syntax")

        start = self._evaluate_literal(start_token)
        end = self._evaluate_literal(end_token)

        # Capture tokens until SEMI (to form 1 complete statement)
        body_tokens = []
        while True:
            tok = self.lexer.token()
            if tok is None:
                break
            body_tokens.append(tok)
            if tok.type == 'SEMI':
                break

        for i in range(start, end):
            self.environment.define(var_token.value, i)
            self.lexer._tokens = body_tokens + self.lexer._tokens
            self._run_next_statement()

    def _handle_while(self):
        # Parse condition: x < 3
        cond_tokens = [self.lexer.token(), self.lexer.token(), self.lexer.token()]
        colon_token = self.lexer.token()
        if colon_token.type != 'COLON':
            raise KillaSyntaxError("Missing ':' after while condition")

        # Capture body tokens until VAR/FOR/IF/WHILE or EOF
        body_tokens = []
        while True:
            tok = self.lexer.token()
            if tok is None or tok.type in ('VAR', 'FOR', 'WHILE', 'IF'):
                if tok:
                    self.lexer._tokens.insert(0, tok)
                break
            body_tokens.append(tok)

        while True:
            # Check condition
            left_val = self._evaluate_literal(cond_tokens[0])
            op = cond_tokens[1].value
            right_val = self._evaluate_literal(cond_tokens[2])
            if not self.eval_op(left_val, op, right_val):
                break

            # Restore a fresh copy of body tokens
            self.lexer._tokens = body_tokens.copy() + self.lexer._tokens

            # Run all statements in the body
            remaining = body_tokens.copy()
            while remaining:
                self._run_next_statement()
                # Remove tokens we just processed
                while remaining:
                    t = remaining.pop(0)
                    if t.type == 'SEMI':
                        break

    def _handle_func_call(self, func_name_token):
        args = []

        # Collect arguments until we hit SEMI
        while True:
            tok = self.lexer.token()
            if tok is None:
                break
            if tok.type == 'SEMI':
                break
            args.append(self._evaluate_literal(tok))

        # Lookup function
        func = self.environment.get(func_name_token.value)
        if not isinstance(func, Function):
            raise KillaRuntimeError(f"'{func_name_token.value}' is not a function")

        # Call the function with evaluated arguments
        result = func.call(self, args)
        #print(f"[CALL] {func_name_token.value}({', '.join(str(a) for a in args)})")
        #if result is not None:
        #    print(f"[FUNC RETURN] {result}")

    def _handle_func_def(self):
        name_token = self.lexer.token()
        params = []

        # Collect parameters until ':'
        while True:
            tok = self.lexer.token()
            if tok is None:
                raise KillaSyntaxError("Unexpected end of input in function definition")
            if tok.type == 'COLON':
                break
            if tok.type == 'ID':
                params.append(tok.value)

        # Collect body tokens until SEMI
        body_tokens = []
        while True:
            tok = self.lexer.token()
            if tok is None or tok.type == 'SEMI':
                break
            body_tokens.append(tok)

        func = Function(name_token.value, params, body_tokens, self.environment)
        self.environment.define(name_token.value, func)
        # print(f"[DEFINE] func {name_token.value}({', '.join(params)})")

    def _handle_return(self):
        if not isinstance(self.environment, Environment):
            raise KillaSyntaxError("return outside function")

        expr_token = self.lexer.token()
        semi_token = self.lexer.token()

        if semi_token is None or semi_token.type != 'SEMI':
            raise KillaSyntaxError("Missing ';' after return statement")

        value = self._evaluate_literal(expr_token)
        raise ReturnException(value)

    def parse_expression(self):
        left = self._parse_unary()

        while self.lexer._tokens:
            next_tok = self.lexer._tokens[0]
            if next_tok.type in ('SEMI', 'COLON'):
                break

            if next_tok.type in ('PLUS', 'MINUS', 'TIMES', 'DIVISION', 'DIVISIBILITY',
                                 'GT', 'LT', 'GE', 'LE', 'EQUAL_EQUAL', 'NOTEQUAL',
                                 'AND', 'OR'):
                op = self.lexer.token()
                right = self._parse_unary()
                left = BinaryExpression(left, op.value, right)
            else:
                break

        return left

    def _parse_unary(self):
        tok = self.lexer.token()
        if tok.type == 'NOT':
            operand = self._parse_unary()
            return UnaryExpression('not', operand)
        elif tok.type == 'ID':
            # 檢查是否為 function call
            next_tok = self.lexer._tokens[0] if self.lexer._tokens else None
            if next_tok and next_tok.type == 'LPAREN':
                self.lexer.token()  # consume '('
                args = []

                if self.lexer._tokens[0].type != 'RPAREN':
                    while True:
                        args.append(self.parse_expression())
                        if self.lexer._tokens[0].type == 'DOT':
                            self.lexer.token()  # consume ','
                        else:
                            break

                rparen = self.lexer.token()
                if rparen.type != 'RPAREN':
                    raise SyntaxError("Expected ')' after function arguments")

                return FunctionCall(tok.value, args)
            else:
                return Variable(tok.value)
        else:
            return self._literal_to_ast(tok)

    def _parse_if(self):
        # Parse full expression like: x > 4
        condition = self.parse_expression()

        # Expect colon (same line)
        colon = self.lexer.token()
        if not colon or colon.type != 'COLON':
            raise KillaSyntaxError(f"Expected ':' after if condition, got {colon.type if colon else 'EOF'}")

        then_stmt = self._parse_statement()

        # Check for optional else
        next_tok = self.lexer._tokens[0] if self.lexer._tokens else None
        else_stmt = None
        if next_tok and next_tok.type == 'ELSE':
            self.lexer.token()  # consume 'else'
            colon2 = self.lexer.token()
            if not colon2 or colon2.type != 'COLON':
                raise KillaSyntaxError("Missing ':' after else")
            else_stmt = self._parse_statement()

        return IfStatement(condition, [then_stmt], [else_stmt] if else_stmt else None)

    def _parse_assignment(self, id_token):
        eq_token = self.lexer.token()
        if not eq_token or eq_token.type != 'EQUAL':
            raise KillaSyntaxError("Expected '=' in assignment")

        expr = self.parse_expression()  # ✅ handles sum + i

        semi_token = self.lexer.token()
        if not semi_token or semi_token.type != 'SEMI':
            raise KillaSyntaxError("Missing ';' after assignment")

        return Assignment(id_token.value, expr)

    def _parse_func_def(self):
        name_token = self.lexer.token()
        params = []

        # collect param1 param2 ... until COLON
        while True:
            tok = self.lexer.token()
            if not tok:
                raise KillaSyntaxError("Unexpected EOF in function def")
            if tok.type == 'COLON':
                break
            if tok.type == 'ID':
                params.append(tok.value)

        # collect body until SEMI
        body = []
        while True:
            if not self.lexer._tokens:
                raise KillaSyntaxError("Expected 'end' to close function definition")
            peek = self.lexer._tokens[0]
            if peek.type == 'END':
                self.lexer.token()  # consume 'end'
                break
            stmt = self._parse_statement()
            body.append(stmt)

        return FunctionDeclaration(name_token.value, params, body)

    def parse_and_build_ast(self, code):
        self.lexer.input(code)
        statements = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            if tok.type == 'VAR':
                statements.append(self._parse_var_declaration())
            elif tok.type == 'ID':
                next_tok = self.lexer._tokens[0] if self.lexer._tokens else None
                if next_tok and next_tok.type == 'EQUAL':
                    statements.append(self._parse_assignment(tok))
                else:
                    statements.append(self._parse_func_call(tok))
            elif tok.type == 'PRINT':
                statements.append(self._parse_print())
            elif tok.type == 'FUNC':
                statements.append(self._parse_func_def())
            elif tok.type == 'IF':
                statements.append(self._parse_if())
            elif tok.type == 'FOR':
                statements.append(self._parse_for())
            elif tok.type == 'WHILE':
                statements.append(self._parse_while())
            elif tok.type == 'SWITCH':
                statements.append(self._parse_switch())
            elif tok.type == 'BREAK':
                statements.append(self._parse_break())
            else:
                raise KillaSyntaxError(f"Unknown token: {tok.type}")
        return Program(statements)
    def _parse_for(self):
        var_token = self.lexer.token()
        if var_token.type != 'ID':
            raise KillaSyntaxError("Expected loop variable after 'for'")
        in_token = self.lexer.token()
        if not in_token or in_token.type != 'IN':
            raise KillaSyntaxError("Expected 'in' after for variable")
        range_token = self.lexer.token()
        if not range_token or range_token.type != 'RANGE':
            raise KillaSyntaxError("Expected 'range' after 'in'")
        start_token = self.lexer.token()
        end_token = self.lexer.token()
        colon_token = self.lexer.token()
        if not colon_token or colon_token.type != 'COLON':
            raise KillaSyntaxError("Expected ':' after for loop range")
        # ✅ collect multi-line body
        body = []
        while self.lexer._tokens:
            peek = self.lexer._tokens[0]
            if peek.type == 'END':  # 🥶 表示區塊結尾
                self.lexer.token()  # consume 'END'
                break
            stmt = self._parse_statement()
            body.append(stmt)
        return ForStatement(
            var_name=var_token.value,
            start_expr=self._literal_to_ast(start_token),
            end_expr=self._literal_to_ast(end_token),
            body=body
        )

    def _parse_while(self):
        condition = self.parse_expression()

        colon = self.lexer.token()
        if not colon or colon.type != 'COLON':
            raise KillaSyntaxError("Expected ':' after while condition")

        # ✅ 改為吃到 END 為止
        body = []
        while self.lexer._tokens:
            peek = self.lexer._tokens[0]
            if peek.type == 'END':  # 🥶 結尾
                self.lexer.token()  # consume 'END'
                break
            stmt = self._parse_statement()
            body.append(stmt)

        return WhileStatement(condition, body)

    def _parse_statement(self):
        tok = self.lexer.token()
        if not tok:
            raise KillaSyntaxError("Unexpected end of input in statement")

        if tok.type == 'VAR':
            return self._parse_var_declaration()
        elif tok.type == 'RETURN':
            return self._parse_return()
        elif tok.type == 'PRINT':
            return self._parse_print()
        elif tok.type == 'ID':
            next_tok = self.lexer._tokens[0] if self.lexer._tokens else None
            if next_tok and next_tok.type == 'EQUAL':
                return self._parse_assignment(tok)
            else:
                return self._parse_func_call(tok)
        elif tok.type == 'IF':
            return self._parse_if()
        elif tok.type == 'BREAK':
            semi = self.lexer.token()
            if not semi or semi.type != 'SEMI':
                raise SyntaxError("Missing ';' after break")
            return BreakStatement()
        elif tok.type == 'CONTINUE':
            semi = self.lexer.token()
            if not semi or semi.type != 'SEMI':
                raise SyntaxError("Missing ';' after continue")
            return ContinueStatement()

        else:
            raise KillaSyntaxError(f"Unexpected token in statement: {tok.type}")

    def _parse_break(self):
        semi = self.lexer.token()
        if not semi or semi.type != 'SEMI':
            raise SyntaxError("Missing ';' after break")
        return BreakStatement()

    def _parse_assignment(self, id_token):
        eq_token = self.lexer.token()
        if not eq_token or eq_token.type != 'EQUAL':
            raise KillaSyntaxError("Expected '=' in assignment")

        expr = self.parse_expression()  # ✅ 使用這個來支持運算式 like sum + i

        semi_token = self.lexer.token()
        if not semi_token or semi_token.type != 'SEMI':
            raise KillaSyntaxError("Missing ';' after assignment")

        return Assignment(id_token.value, expr)

    def _parse_func_call(self, id_token):
        lparen = self.lexer.token()
        if not lparen or lparen.type != 'LPAREN':
            raise KillaSyntaxError("Expected '(' after function name")

        args = []

        # 如果下一個不是 ')', 就解析參數
        if self.lexer._tokens and self.lexer._tokens[0].type != 'RPAREN':
            while True:
                args.append(self.parse_expression())
                if self.lexer._tokens and self.lexer._tokens[0].type == 'DOT':
                    self.lexer.token()  # consume ','
                else:
                    break

        # ✅ 真正吃掉右括號
        rparen = self.lexer.token()
        if not rparen or rparen.type != 'RPAREN':
            raise KillaSyntaxError("Expected ')' after function arguments")

        # ✅ 然後吃掉分號
        semi = self.lexer.token()
        if not semi or semi.type != 'SEMI':
            raise KillaSyntaxError("Missing ';' after function call")

        return FunctionCall(id_token.value, args)

    def _parse_print(self):
        lparen = self.lexer.token()
        if not lparen or lparen.type != 'LPAREN':
            raise KillaSyntaxError("Expected '(' after prt")

        expr = self.parse_expression()

        rparen = self.lexer.token()
        if not rparen or rparen.type != 'RPAREN':
            raise KillaSyntaxError("Expected ')' after expression")

        semi_token = self.lexer.token()
        if not semi_token or semi_token.type != 'SEMI':
            raise KillaSyntaxError("Missing semicolon after print")

        return PrintStatement(expr)

    def _parse_var_declaration(self):
        id_token = self.lexer.token()
        eq_token = self.lexer.token()

        if id_token.type != 'ID' or eq_token.type != 'EQUAL':
            raise KillaSyntaxError("Invalid var declaration")

        # NEW: parse full expression instead of 1 token
        expr = self.parse_expression()

        semi_token = self.lexer.token()
        if semi_token.type != 'SEMI':
            raise KillaSyntaxError("Missing semicolon after variable declaration")

        return VarDeclaration(id_token.value, expr)

    def _literal_to_ast(self, token):
        if token.type == 'NUMBER':
            return Literal(token.value)
        elif token.type == 'STRING':
            return Literal(token.value)
        elif token.type == 'TRUE':
            return Literal(True)
        elif token.type == 'FALSE':
            return Literal(False)
        elif token.type == 'ID':
            return Variable(token.value)
        else:
            raise KillaSyntaxError(f"Unsupported expression: {token.type}")

    def _parse_switch(self):
        switch_expr = self.parse_expression()

        colon = self.lexer.token()
        if not colon or colon.type != 'COLON':
            raise SyntaxError("Expected ':' after switch expression")

        cases = []
        default_case = []

        while self.lexer._tokens:
            tok = self.lexer._tokens[0]

            if tok.type == 'CASE':
                self.lexer.token()  # consume 'case'
                value_token = self.lexer.token()
                value = self._literal_to_ast(value_token)

                colon = self.lexer.token()
                if not colon or colon.type != 'COLON':
                    raise SyntaxError("Expected ':' after case value")

                body = []
                while self.lexer._tokens:
                    if self.lexer._tokens[0].type in ('CASE', 'DEFAULT'):
                        break
                    body.append(self._parse_statement())

                cases.append(CaseClause(value, body))

            elif tok.type == 'DEFAULT':
                self.lexer.token()
                colon = self.lexer.token()
                if not colon or colon.type != 'COLON':
                    raise SyntaxError("Expected ':' after default")

                body = []
                while self.lexer._tokens:
                    if self.lexer._tokens[0].type in ('CASE',):  # switch 沒有結尾 token
                        break
                    body.append(self._parse_statement())

                default_case = body

            else:
                break  # end of switch

        return SwitchStatement(switch_expr, cases, default_case)

    def run_ast(self, code):
        ast = self.parse_and_build_ast(code)
        for stmt in ast.statements:
            self.execute(stmt)

    def execute(self, node):
        if isinstance(node, VarDeclaration):
            value = self.evaluate_expr(node.expr)
            self.environment.define(node.name, value)
            return None
        elif isinstance(node, Assignment):
            value = self.evaluate_expr(node.expr)
            if self.environment.exists(node.name):
                self.environment.assign(node.name, value)
                return None
            else:
                self.environment.define(node.name, value)
                return None
        elif isinstance(node, PrintStatement):
            value = self.evaluate_expr(node.expr)
            print(value)
            return None
        elif isinstance(node, FunctionCall):
            func = self.environment.get(node.name)
            if not isinstance(func, Function):
                raise KillaRuntimeError(f"'{node.name}' is not a function")

            arg_values = [self.evaluate_expr(arg) for arg in node.arguments]
            result = func.call(self, arg_values)
            return result
        elif isinstance(node, ForStatement):
            start = self.evaluate_expr(node.start_expr)
            end = self.evaluate_expr(node.end_expr)
            for i in range(start, end):
                if node.var_name in self.environment.values:
                    self.environment.assign(node.var_name, i)
                else:
                    self.environment.define(node.var_name, i)
                try:
                    for stmt in node.body:
                        self.execute(stmt)
                except BreakException:
                    # print("✅ Break caught, exiting loop")
                    break  # ✅ 正確中止這個 for 迴圈！
                except ContinueException:
                    continue
        elif isinstance(node, IfStatement):
            cond = self.evaluate_expr(node.condition)
            if cond:
                for stmt in node.then_branch:
                    self.execute(stmt)
                    return None
                return None
            elif node.else_branch:
                for stmt in node.else_branch:
                    self.execute(stmt)
            return None
        elif isinstance(node, WhileStatement):
            while self.evaluate_expr(node.condition):
                try:
                    for stmt in node.body:
                        self.execute(stmt)
                except ContinueException:
                    continue
                except BreakException:
                    # print("✅ Break caught, exiting loop")
                    break
            return None
        elif isinstance(node, FunctionDeclaration):
            func = Function(
                name=node.name,
                params=node.params,
                body_tokens=node.body,
                closure=self.environment
            )
            self.environment.define(node.name, func)
            return None
        elif isinstance(node, ReturnStatement):
            value = self.evaluate_expr(node.expr)
            raise KillaReturn(value)
        # 在 execute 裡加這段
        elif isinstance(node, BreakStatement):
            # print("🚨 Break triggered!")
            raise BreakException()
        elif isinstance(node, SwitchStatement):
            switch_val = self.evaluate_expr(node.expr)
            matched = False
            try:
                for case in node.cases:
                    if not matched and self.evaluate_expr(case.value) == switch_val:
                        matched = True  # 從這裡開始執行
                    if matched:
                        for stmt in case.body:
                            self.execute(stmt)
            except BreakException:
                pass  # break 結束 switch

            if not matched and node.default_case:
                try:
                    for stmt in node.default_case:
                        self.execute(stmt)
                except BreakException:
                    return None
            return None
        # 在 execute 裡加入
        elif isinstance(node, ContinueStatement):
            raise ContinueException()
        else:
            raise KillaRuntimeError(f"Unknown AST node type: {type(node).__name__}")

    def evaluate_expr(self, expr):
        if isinstance(expr, Literal):
            return expr.value

        elif isinstance(expr, Variable):
            value = self.environment.get(expr.name)
            # If it's a function, call it (no arguments)
            if isinstance(value, Function):
                return value.call(self, [])
            return value
        elif isinstance(expr, UnaryExpression):
            operand = self.evaluate_expr(expr.operand)
            return self.eval_unary_op(expr.operator, operand)

        elif isinstance(expr, FunctionCall):
            func = self.environment.get(expr.name)
            if not isinstance(func, Function):
                raise KillaRuntimeError(f"'{expr.name}' is not a function")
            arg_values = [self.evaluate_expr(arg) for arg in expr.arguments]
            return func.call(self, arg_values)

        elif isinstance(expr, BinaryExpression):
            left = self.evaluate_expr(expr.left)
            right = self.evaluate_expr(expr.right)
            return self.eval_op(left, expr.operator, right)

        else:
            raise KillaRuntimeError(f"Unknown expression type: {type(expr).__name__}")

    @property
    def tokens(self):
        return self._tokens

    def _parse_return(self):
        expr = self.parse_expression()  # ← this handles full expressions like n * fact n - 1

        semi_token = self.lexer.token()
        if not semi_token or semi_token.type != 'SEMI':
            raise KillaSyntaxError("Missing ';' after return")

        return ReturnStatement(expr)


def run_ast(code):
    interp = KillaInterpreter()
    program = interp.parse_and_build_ast(code)
    for stmt in program.statements:
        try:
            interp.execute(stmt)
        except BreakException:
            KillaRuntimeError("⚠️ Warning: 'brk' used outside of loop (ignored)")
        except ContinueException:
            KillaRuntimeError("⚠️ Warning: 'continue' used outside of loop (ignored)")



if __name__ == '__main__':
    interp = KillaInterpreter()
    try:
        while True:
            code = input("killa_input> ")
            if code.strip() == '':
                continue
            interp.parse_and_run(code)
    except (EOFError, KeyboardInterrupt):
        print("\nExiting Killa")
