import re

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.token_specs = [
            ('NUMBER',   r'\d+'),          # Integer
            ('ID',       r'[a-zA-Z_]\w*'), # Identifiers
            ('OP',       r'[+\-*/]'),      # Arithmetic operators
            ('ASSIGN',   r'='),            # Assignment operator
            ('LPAREN',   r'\('),           # Left parenthesis
            ('RPAREN',   r'\)'),           # Right parenthesis
            ('LBRACE',   r'\{'),           # Left brace
            ('RBRACE',   r'\}'),           # Right brace
            ('SEMI',     r';'),            # Semicolon
            ('IF',       r'if'),           # if keyword
            ('ELSE',     r'else'),         # else keyword
            ('FOR',      r'for'),          # for keyword
            ('RETURN',   r'return'),       # return keyword
            ('GT',       r'>'),            # Greater than
            ('LT',       r'<'),            # Less than
            ('SKIP',     r'[ \t\n]+'),     # Skip over spaces and tabs
            ('MISMATCH', r'.'),            # Any other character
        ]
        self.regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specs)

    def tokenize(self):
        for mo in re.finditer(self.regex, self.source_code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUMBER':
                value = int(value)
            elif kind == 'ID' and value in {'if', 'else', 'for', 'return'}:
                kind = value.upper()
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected')
            self.tokens.append((kind, value))
        self.tokens.append(('EOF', 'EOF'))
        return self.tokens

# Example usage
lexer = Lexer("a = 5; for (i = 0; i < 10; i = i + 1) { c = c + 1; } if (c > 10) { d = c - 1; } else { d = c + 1; } return d;")
tokens = lexer.tokenize()
for token in tokens:
    print(token)
