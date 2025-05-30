# killa_Lexer.py — 使用 re 的 Lexer（完全取代 PLY）

import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'lineno', 'lexpos'])


class Lexer:
    def __init__(self):
        self.lineno = 1
        self.pos = 0
        self.text = ''
        self.reserved = {
            'id': 'ID', 'for': 'FOR', 'while': 'WHILE',
            'if': 'IF', 'else': 'ELSE', 'brk': 'BREAK',
            'in': 'IN', 'range': 'RANGE', 'prt': 'PRINT',
            'ret': 'RETURN', 'switch': 'SWITCH',
            'case': 'CASE', 'default': 'DEFAULT',
            'var': 'VAR', 'func': 'FUNC',
        }

        self.token_spec = [
            ('NUMBER', r'\d+'),
            ('STRING', r'(\"([^\\\n]|(\\.))*?\"|\'([^\\\n]|(\\.))*?\')'),
            ('GE', r'>='),
            ('LE', r'<='),
            ('EQUAL_EQUAL', r'=='),
            ('NOTEQUAL', r'!='),
            ('GT', r'>'),
            ('LT', r'<'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('TIMES', r'\*'),
            ('DIVISIBILITY', r'\/\/'),
            ('DIVISION', r'/'),
            ('EQUAL', r'='),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('DOT', r','),
            ('SEMI', r';'),
            ('COLON', r':'),
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('COMMENT', r'\#.*'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),
            ('MISMATCH', r'.'),
        ]

        self.token_re = re.compile('|'.join(f'(?P<{name}>{regex})' for name, regex in self.token_spec))
        self._tokens = []

        # 令 parser 可以直接使用的 token 名稱
        self.tokens = tuple(
            {name for name, _ in self.token_spec if name not in ('SKIP', 'MISMATCH', 'NEWLINE', 'COMMENT')} | set(
                self.reserved.values()))

    def build(self):  # 兼容 PLY 的 interface
        return self

    def input(self, text):
        self.text = text
        self.pos = 0
        self.lineno = 1
        self._tokens = list(self._generate_tokens())

    def token(self):
        if not self._tokens:
            return None
        return self._tokens.pop(0)

    def _generate_tokens(self):
        while self.pos < len(self.text):
            match = self.token_re.match(self.text, self.pos)
            if not match:
                raise SyntaxError(f"Unknown token at pos {self.pos}")
            kind = match.lastgroup
            value = match.group()
            lexpos = self.pos
            self.pos = match.end()

            if kind == 'NEWLINE':
                self.lineno += 1
                continue
            elif kind in ('SKIP', 'COMMENT'):
                continue
            elif kind == 'ID':
                kind = self.reserved.get(value, 'ID')
            elif kind == 'NUMBER':
                value = int(value)
            elif kind == 'STRING':
                value = value[1:-1]
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Unexpected character {value} at line {self.lineno}")

            yield Token(kind, value, self.lineno, lexpos)
