import sys


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def next_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token):
        if self.next_token() == token:
            self.pos += 1
        else:
            raise SyntaxError(f"Expected {token}, got {self.next_token()}")

    def parse_P(self):
        self.parse_E()
        if self.next_token() != '$':
            raise SyntaxError("Expected $ at the end")
        self.eat('$')

    def parse_E(self):
        tok = self.next_token()

        if tok is None:
            raise SyntaxError("Unexpected end of input")

        if tok in 'abcdefghijklmnopqrstuvwxyz':
            self.eat(tok)

        elif tok == "'":
            self.eat("'")
            self.parse_E()

        elif tok == '(':
            self.eat('(')
            self.parse_E()
            self.parse_Es()
            if self.next_token() != ')':
                raise SyntaxError("Expected )")
            self.eat(')')

        else:
            raise SyntaxError(f"Invalid token in E: {tok}")

    def parse_Es(self):
        tok = self.next_token()

        # ε (空字串)：如果遇到 ')' 就是空
        if tok == ')':
            return

        # 嘗試解析 E，再遞迴解析 Es
        self.parse_E()
        self.parse_Es()


# 驗證輸入是否為合法句子
def check_input(line):
    tokens = line.strip().split()
    try:
        parser = Parser(tokens)
        parser.parse_P()
        if parser.pos != len(tokens):
            print("error")
        else:
            print("accept")
    except SyntaxError:
        print("error")


if __name__ == "__main__":
    for line in sys.stdin:
        if not line.strip():
            continue
        check_input(line)
