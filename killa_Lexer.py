import ply.lex as lex

class Lexer:
    def __init__(self):
        # 建立 Lexer
        self.lexer = lex.lex(module=self)

    # 定義 Token 類型
    tokens = (
        'NUMBER',    # 數字
        'PLUS',      # +
        'MINUS',     # -
        'TIMES',     # *
        'DIVISION',    # /
        'LPAREN',    # (
        'RPAREN',    # )
        'DIVISIBILITY', # //
    )

    # 定義 Token 的正則規則（t_ 開頭）
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVISION = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_DIVISIBILITY = r'//'
    # 定義數字（需要處理數值轉換）
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)  # 轉換為整數
        return t

    # 忽略空格
    t_ignore = ' \t'

    # 錯誤處理
    def t_error(self, t):
        print(f"Error code: {t.value[0]}")
        t.lexer.skip(1)

    # 讀取輸入
    def input(self, data):
        self.lexer.input(data)

    # 取得 Token
    def token(self):
        return self.lexer.token()

# 測試 Lexer
if __name__ == "__main__":
    lexer = Lexer()
    data = "3+4*(2-1)//4"
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
