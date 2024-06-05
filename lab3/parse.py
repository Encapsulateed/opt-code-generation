from lexer import Lexer, Token
from my_ast import *

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def eat(self, token_type: str):
        if self.current_token and self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()
        else:
            self.error(token_type)

    def error(self, expected_type: str):
        current_value = self.current_token.value if self.current_token else "None"
        raise Exception(f"Expected token {expected_type}, got {current_value} ({self.current_token.type if self.current_token else 'None'})")

    def parse(self) -> Program:
        statements = self.parse_statements()
        return Program(statements)

    def parse_statements(self) -> Statements:
        statements = []
        while self.current_token and self.current_token.type != 'RBRACE':
            statements.append(self.parse_statement())
            if self.current_token is not None and self.current_token.type == 'SEMICOLON':
                self.eat('SEMICOLON')
        return Statements(statements)

    def parse_statement(self) -> Statement:
        if self.current_token.type == 'IDENT':
            return Statement(self.parse_assignment())
        elif self.current_token.type == 'IF':
            return Statement(self.parse_if_statement())
        elif self.current_token.type == 'FOR':
            return Statement(self.parse_for_statement())
        elif self.current_token.type == 'RETURN':
            return Statement(self.parse_return_statement())
        else:
            self.error('statement')

    def parse_assignment(self) -> Assignment:
        ident = self.current_token.value
        self.eat('IDENT')
        self.eat('ASSIGN')
        value = self.parse_id_or_num()
        return Assignment(ident, value)

    def parse_if_statement(self) -> IfStatement:
        self.eat('IF')
        self.eat('LPAREN')
        expr = self.parse_expr()
        self.eat('RPAREN')
        self.eat('LBRACE')
        statements = self.parse_statements()
        self.eat('RBRACE')
        return IfStatement(expr, statements)

    def parse_for_statement(self) -> ForStatement:
        self.eat('FOR')
        self.eat('LPAREN')
        assignment = self.parse_assignment()
        self.eat('SEMICOLON')
        expr1 = self.parse_expr()
        self.eat('SEMICOLON')
        expr2 = self.parse_expr()
        self.eat('RPAREN')
        self.eat('LBRACE')
        statements = self.parse_statements()
        self.eat('RBRACE')
        return ForStatement(assignment, expr1, expr2, statements)

    def parse_return_statement(self) -> ReturnStatement:
        self.eat('RETURN')
        value = self.parse_id_or_num()
        return ReturnStatement(value)

    def parse_expr(self) -> Expr:
        left = self.parse_id_or_num()
        if self.current_token.type in ('LOGIC_OP', 'ARITHM_OP'):
            operator = self.parse_operator()
            right = self.parse_id_or_num()
            if self.current_token.type == 'ASSIGN':
                self.eat('ASSIGN')
                comparison = self.parse_id_or_num()
                return Expr(left, operator, right, comparison)
            return Expr(left, operator, right)
        else:
            self.error('operator')

    def parse_id_or_num(self) -> IdOrNum:
        if self.current_token.type == 'IDENT':
            value = self.current_token.value
            self.eat('IDENT')
            return IdOrNum(value)
        elif self.current_token.type == 'NUMBER':
            value = int(self.current_token.value)
            self.eat('NUMBER')
            return IdOrNum(value)
        else:
            self.error('IDENT or NUMBER')

    def parse_operator(self) -> Union[LogicOp, ArithmOp]:
        if self.current_token.type == 'LOGIC_OP':
            op = LogicOp(self.current_token.value)
        elif self.current_token.type == 'ARITHM_OP':
            op = ArithmOp(self.current_token.value)
        else:
            self.error('operator')
        self.eat(self.current_token.type)
        return op

# Example usage
if __name__ == "__main__":
    code = """
    x = 10;
    IF (x > 5) {
        FOR(i = 0;i < 2 ;i+=1){}
        RETURN x;
    }
    """
    lexer = Lexer(code)
    parser = Parser(lexer)
    program = parser.parse()
    print(program)
