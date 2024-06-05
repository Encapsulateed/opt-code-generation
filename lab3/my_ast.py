from dataclasses import dataclass, field
from typing import List, Optional, Union, Iterator

@dataclass
class Program:
    statements: 'Statements'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Program:\n" + self.statements.__str__(level + 1)

@dataclass
class Statements:
    statements: List['Statement']

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Statements:\n" + '\n'.join(s.__str__(level + 1) for s in self.statements)

    def __iter__(self) -> Iterator['Statement']:
        return iter(self.statements)

@dataclass
class Statement:
    statement: Union['Assignment', 'IfStatement', 'ForStatement', 'ReturnStatement']

    def __str__(self, level=0):
        return self.statement.__str__(level)

@dataclass
class Assignment:
    ident: str
    value: 'IdOrNum'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Assignment: {self.ident} = {self.value}"

@dataclass
class IfStatement:
    expr: 'Expr'
    statements: Statements

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return (f"{indent}IfStatement:\n"
                f"{self.expr.__str__(level + 1)}\n"
                f"{self.statements.__str__(level + 1)}")

@dataclass
class ForStatement:
    assignment: Assignment
    expr1: 'Expr'
    expr2: 'Expr'
    statements: Statements

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return (f"{indent}ForStatement:\n"
                f"{self.assignment.__str__(level + 1)}\n"
                f"{self.expr1.__str__(level + 1)}\n"
                f"{self.expr2.__str__(level + 1)}\n"
                f"{self.statements.__str__(level + 1)}")

@dataclass
class ReturnStatement:
    value: 'IdOrNum'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}ReturnStatement: {self.value}"

@dataclass
class Expr:
    left: 'IdOrNum'
    operator: Union['LogicOp', 'ArithmOp']
    right: 'IdOrNum'
    comparison: Optional['IdOrNum'] = None

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        comparison_str = f" == {self.comparison}" if self.comparison else ""
        return f"{indent}Expr: {self.left} {self.operator} {self.right}{comparison_str}"

@dataclass
class IdOrNum:
    value: Union[str, int]

    def __str__(self, level=0):
        return str(self.value)

@dataclass
class LogicOp:
    operator: str

    def __str__(self, level=0):
        return self.operator

@dataclass
class ArithmOp:
    operator: str

    def __str__(self, level=0):
        return self.operator
