import ply.lex as lex


class Lexer:
    def __init__(self):
        # 定義 Token 類型 dict型別(用於特殊符號)
        self.reserved = {
            'id':'ID',
            'if': 'IF',
            'else': 'ELSE',
            'equal':'EQUAL'
        }
        self.tokens = (
            'NUMBER',  # 數字
            'PLUS',  # +
            'MINUS',  # -
            'TIMES',  # *
            'DIVISION',  # /
            'LPAREN',  # (
            'RPAREN',  # )
            'DIVISIBILITY',  # //
        ) + tuple(self.reserved.values()) # 轉換成tuple

        # 定義 Token 規則（t_ 開頭）
        self.t_PLUS = r'\+'
        self.t_MINUS = r'-'
        self.t_TIMES = r'\*'
        self.t_DIVISION = r'/'
        self.t_LPAREN = r'\('
        self.t_RPAREN = r'\)'
        self.t_DIVISIBILITY = r'//'
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
    def t_EQUAL(self,t):
        r'='
        t.value = self.reserved.get(t.value,'EQUAL')
        return t
    # 取得 Token
    def token(self):
        return self.lexer.token()


# 測試 Lexer
if __name__ == "__main__":
    lexer = Lexer()
    data = "x=1+2"
    lexer.input(data)
    while True:
        token = lexer.token()
        if not token:
            break
        print(token)
