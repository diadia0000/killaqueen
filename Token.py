from ply.lex import *
from ply.yacc import *


class Token(object):
    def __init__(self):
        # 初始化token
        self.token = ('NUMBER', 'PLUS', 'MINUS', 'TIMES',
                      'DIV', 'LPAREN', 'RPAREN', 'EXPR'
        )
        ''' 解釋符號 '''
        self.value = None
        self.t_PLUS = r'\+'
        self.t_MINUS = r'-'
        self.t_TIMES = r'\*'
        self.t_DIV = r'/'
        self.t_LPAREN = r'\('
        self.t_RPAREN = r'\)'
        self.t_Ignore = ' \t'

    # 定義數字（需要處理數值轉換）
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)  # 轉換為整數
        return t

    # 忽略空格
    def t_IGNORE(self, t):
        self.t_ignore = ' \t'

    # 處理加號
    def t_PLUS(self, t):
        pass

    # 處理錯誤
    def t_error(self, t):
        print(f"非法字元: {t.value[0]}")
        t.lexer.skip(1)


# 建立 Lexer
lexer = lex.lex()

# 測試 Lexer
if __name__ == "__main__":
    data = "3 + 4 * (2 - 1)"
    lexer.input(data)
    for tok in lexer:
        print(tok)
