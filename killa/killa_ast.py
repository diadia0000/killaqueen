# Abstract Syntax Tree (AST) node classes for Killa Language

class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class VarDeclaration(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class Assignment(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class PrintStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr


class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class ForStatement(ASTNode):
    def __init__(self, var_name, start_expr, end_expr, body):
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.body = body


class FunctionDeclaration(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class ReturnStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr


class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class BinaryExpression(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class Literal(ASTNode):
    def __init__(self, value):
        self.value = value


class Variable(ASTNode):
    def __init__(self, name):
        self.name = name


class SwitchStatement(ASTNode):
    def __init__(self, expr, cases, default_case):
        self.expr = expr
        self.cases = cases  # List of CaseClause
        self.default_case = default_case  # List of statements


class CaseClause(ASTNode):
    def __init__(self, value, body):
        self.value = value
        self.body = body  # List[ASTNode]


class BreakStatement(ASTNode):
    pass
