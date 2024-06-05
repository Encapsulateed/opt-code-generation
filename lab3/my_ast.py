from lexer import Lexer

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        return "Program(" + ", ".join(str(stmt) for stmt in self.statements) + ")"

class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"Assignment({self.name}, {self.value})"

class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return f"BinaryOperation({self.left}, {self.operator}, {self.right})"

class IfStatement(ASTNode):
    def __init__(self, condition, true_block, false_block):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

    def __str__(self):
        return f"IfStatement({self.condition}, {self.true_block}, {self.false_block})"

class ForStatement(ASTNode):
    def __init__(self, init, condition, increment, body):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body

    def __str__(self):
        return f"ForStatement({self.init}, {self.condition}, {self.increment}, {self.body})"

class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"ReturnStatement({self.value})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        statements = []
        while not self.match('EOF'):
            statements.append(self.statement())
        return Program(statements)

    def statement(self):
        if self.match('ID'):
            return self.assignment()
        elif self.match('IF'):
            return self.if_statement()
        elif self.match('FOR'):
            return self.for_statement()
        elif self.match('RETURN'):
            return self.return_statement()
        else:
            raise SyntaxError("Unexpected token")

    def assignment(self):

        name = self.previous()[1]
        self.consume('ASSIGN')
        value = self.expression()
        self.consume('SEMI')
        return Assignment(name, value)

    def if_statement(self):
        self.consume('LPAREN')
        condition = self.expression()
        self.consume('RPAREN')
        self.consume('LBRACE')
        true_block = []
        while not self.match('RBRACE'):
            true_block.append(self.statement())
        self.consume('RBRACE')
        false_block = []
        if self.match('ELSE'):
            self.consume('LBRACE')
            while not self.match('RBRACE'):
                false_block.append(self.statement())
            self.consume('RBRACE')
        return IfStatement(condition, true_block, false_block)

    def for_statement(self):
        self.consume('LPAREN')
        init = self.assignment()
        condition = self.expression()
        self.consume('SEMI')
        increment = self.assignment()
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while not self.match('RBRACE'):
            body.append(self.statement())
        self.consume('RBRACE')
        return ForStatement(init, condition, increment, body)

    def return_statement(self):
        value = self.expression()
        self.consume('SEMI')
        return ReturnStatement(value)

    def expression(self):
        left = self.term()
        while self.match('OP') or self.match('GT') or self.match('LT'):
            operator = self.previous()[1]
            right = self.term()
            left = BinaryOperation(left, operator, right)
        return left

    def term(self):
        if self.match('NUMBER'):
            return self.previous()[1]
        elif self.match('ID'):
            return self.previous()[1]
        elif self.match('LPAREN'):
            expr = self.expression()
            self.consume('RPAREN')
            return expr
        else:
            raise SyntaxError(f"Unexpected token, given {self.tokens[self.pos]}")

    def match(self, kind):
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == kind:
            self.pos += 1
            return True
        return False

    def consume(self, kind):
        if self.match(kind):
            return self.previous()
        raise SyntaxError(f"Expected {kind}, but given {self.tokens[self.pos]}")

    def previous(self):
        return self.tokens[self.pos - 1]

lexer = Lexer("if (c > 10) { d = c - 1; }")

# Example usage
tokens = lexer.tokenize()
for tok in tokens:
    print(tok)
parser = Parser(tokens)
ast = parser.parse()
print(ast)
