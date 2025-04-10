import ply.lex as lex


class Lexer:
    def __init__(self):
        # 定義 Token 類型 dict型別(用於特殊符號)
        self.reserved = {
            'id': 'ID',
            'for': 'FOR',
            'while': 'WHILE',
            'if': 'IF',
            'else': 'ELSE',
            'brk': 'BREAK',
            'in': 'IN',
            'range': 'RANGE',
            'prt': 'PRINT',
            'ret': 'RETURN',
            'switch': 'SWITCH',
            'case': 'CASE',
            'default': 'DEFAULT',
            'var': 'VAR',
            'func': 'FUNC',
        }
        self.tokens = (
            'NUMBER',  # 數字
            'GREATER_THEN_EQUAL',  # >=
            'GREATER_THEN',  # >
            'LESS_THEN_EQUAL',  # <
            'LESS_THEN',  # <=
            'PLUSPLUS',  # ++
            'PLUS',  # +
            'MINUS',  # -
            'TIMES',  # *
            'DIVISION',  # /
            'LPAREN',  # (
            'RPAREN',  # )
            'DIVISIBILITY',  # //
            'EQUAL',  # =
            'dot', # ,
        ) + tuple(self.reserved.values())  # 轉換成tuple

        # 定義 Token 規則（t_ 開頭）
        self.t_PLUS = r'\+'
        self.t_MINUS = r'\-'
        self.t_TIMES = r'\*'
        self.t_DIVISION = r'/'
        self.t_LPAREN = r'\('
        self.t_RPAREN = r'\)'
        self.t_DIVISIBILITY = r'\/\/'
        self.t_EQUAL = r'='
        self.t_PLUSPLUS = r'\+\+'
        self.t_GREATER_THEN_EQUAL = r'>='
        self.t_GREATER_THEN = r'>'
        self.t_LESS_THEN_EQUAL = r'<='
        self.t_LESS_THEN = r'<'
        self.t_dot = r','
        # 忽略空格
        self.t_ignore = ' \t'
        # 建立 Lexer
        self.lexer = lex.lex(module=self)

    # 定義數字（需要處理數值轉換）
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)  # 轉換為整數
        return t

    # 錯誤處理
    def t_error(self, t):
        print(f"Error code: {t.value[0]}")
        t.lexer.skip(1)

    # 讀取輸入
    def input(self, data):
        self.lexer.input(data)

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # 取得 Token
    def token(self):
        return self.lexer.token()


# test Lexer
if __name__ == "__main__":
    lexer = Lexer()
    data = ("var x,"
            "var y = 10,")
    lexer.input(data)
    while True:
        token = lexer.token()
        if not token:
            break
        print(token)
