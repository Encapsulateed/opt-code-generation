import re
from typing import Iterator, Optional, List

# Token types
TOKEN_TYPES = [
    ('IF', r'\bif\b'),
    ('FOR', r'\bfor\b'),
    ('RETURN', r'\breturn\b'),
    ('IDENT', r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'),
    ('NUMBER', r'\b\d+\b'),
    ('ASSIGN', r'='),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('SEMICOLON', r';'),
    ('LOGIC_OP', r'(<=|>=|==|>|<|\+=)'),
    ('ARITHM_OP', r'(\+|\-|\*|\/)'),
    ('WHITESPACE', r'\s+'),
]

# Compile the regex patterns with case-insensitive flag
TOKEN_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
TOKEN_PATTERN = re.compile(TOKEN_REGEX, re.IGNORECASE)

class Token:
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token(type={self.type}, value='{self.value}')"

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.tokens = self.tokenize(text)
        self._index = 0
        self.current_token = None

    def tokenize(self, text: str) -> List[Token]:
        tokens = []
        for match in TOKEN_PATTERN.finditer(text):
            for name, _ in TOKEN_TYPES:
                value = match.group(name)
                if value is not None:
                    if name != 'WHITESPACE':  # Ignore whitespace tokens
                        tokens.append(Token(name, value))
                    break
        return tokens

    def __iter__(self) -> Iterator[Token]:
        self._index = 0
        return self

    def __next__(self) -> Token:
        if self._index < len(self.tokens):
            self.current_token = self.tokens[self._index]
            self._index += 1
            return self.current_token
        else:
            raise StopIteration

    def next_token(self) -> Optional[Token]:
        try:
            return next(self)
        except StopIteration:
            return None

# Example usage
code = """
x = 10;
IF (x > 5) {
    RETURN x;
}
"""
lexer = Lexer(code)

while (token := lexer.next_token()) is not None:
    print(token)
