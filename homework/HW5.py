class ASTNode:
    def __init__(self, value, left=None, right=None):
        self.value = value  # '+', '-', '*', '/', or number
        self.left = left
        self.right = right


def tokenize(expression: str):
    tokens = []
    i = 0
    while i < len(expression):
        if expression[i].isspace():
            i += 1
        elif expression[i] in '+-*/()':
            tokens.append(expression[i])
            i += 1
        elif expression[i].isdigit():
            num = expression[i]
            i += 1
            while i < len(expression) and expression[i].isdigit():
                num += expression[i]
                i += 1
            tokens.append(num)
        else:
            raise ValueError(f"Unknown character: {expression[i]}")
    return tokens


# 遞迴下降解析器
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self):
        token = self.peek()
        if token is not None:
            self.pos += 1
        return token

    # Grammar:
    # expr    := term (( '+' | '-' ) term)*
    # term    := factor (( '*' | '/' ) factor)*
    # factor  := NUMBER | '(' expr ')'

    def parse(self):
        return self.expr()

    def expr(self):
        node = self.term()
        while self.peek() in ('+', '-'):
            op = self.consume()
            right = self.term()
            node = ASTNode(op, node, right)
        return node

    def term(self):
        node = self.factor()
        while self.peek() in ('*', '/'):
            op = self.consume()
            right = self.factor()
            node = ASTNode(op, node, right)
        return node

    def factor(self):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of input")

        if token == '(':
            self.consume()  # consume '('
            node = self.expr()
            if self.consume() != ')':
                raise ValueError("Expected ')'")
            return node
        elif token.isdigit():
            self.consume()
            return ASTNode(token)
        else:
            raise ValueError(f"Unexpected token: {token}")


def print_ast(node: ASTNode, indent: int = 0):
    print('  ' * indent + str(node.value))
    if node.left:
        print_ast(node.left, indent + 1)
    if node.right:
        print_ast(node.right, indent + 1)


# Main program
if __name__ == "__main__":
    expr = input()
    tokens = tokenize(expr)
    parser = Parser(tokens)
    ast_root = parser.parse()
    print_ast(ast_root)
