from dataclasses import dataclass, field
from typing import List, Optional, Union, Iterator
import llvmlite.ir as ir

@dataclass
class Program:
    statements: 'Statements'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Program:\n" + self.statements.__str__(level + 1)

    def codegen(self, module, builder):
        self.statements.codegen(module, builder)

@dataclass
class Statements:
    statements: List['Statement']

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Statements:\n" + '\n'.join(s.__str__(level + 1) for s in self.statements)

    def __iter__(self) -> Iterator['Statement']:
        return iter(self.statements)

    def codegen(self, module, builder):
        for statement in self.statements:
            statement.codegen(module, builder)

@dataclass
class Statement:
    statement: Union['Assignment', 'IfStatement', 'ForStatement', 'ReturnStatement']

    def __str__(self, level=0):
        return self.statement.__str__(level)

    def codegen(self, module, builder):
        self.statement.codegen(module, builder)

@dataclass
class Assignment:
    ident: str
    value: 'IdOrNum'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Assignment: {self.ident} = {self.value}"

    def codegen(self, module, builder):
        value = self.value.codegen(module, builder)
        ptr = builder.alloca(value.type, name=self.ident)
        builder.store(value, ptr)
        module.globals[self.ident] = ptr  # Save the pointer in the module's global scope
        return ptr

@dataclass
class IfStatement:
    expr: 'Expr'
    statements: Statements

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return (f"{indent}IfStatement:\n"
                f"{self.expr.__str__(level + 1)}\n"
                f"{self.statements.__str__(level + 1)}")

    def codegen(self, module, builder):
        cond = self.expr.codegen(module, builder)
        then_block = builder.function.append_basic_block(name="then")
        merge_block = builder.function.append_basic_block(name="ifcont")

        builder.cbranch(cond, then_block, merge_block)

        builder.position_at_end(then_block)
        self.statements.codegen(module, builder)
        if not builder.block.is_terminated:
            builder.branch(merge_block)

        builder.position_at_end(merge_block)

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

    def codegen(self, module, builder):
        self.assignment.codegen(module, builder)
        loop_block = builder.function.append_basic_block(name="loop")
        after_block = builder.function.append_basic_block(name="afterloop")

        builder.branch(loop_block)
        builder.position_at_end(loop_block)

        cond = self.expr1.codegen(module, builder)
        with builder.if_then(cond):
            self.statements.codegen(module, builder)
            self.expr2.codegen(module, builder)
            if not builder.block.is_terminated:
                builder.branch(loop_block)

        if not builder.block.is_terminated:
            builder.branch(after_block)

        builder.position_at_end(after_block)

@dataclass
class ReturnStatement:
    value: 'IdOrNum'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}ReturnStatement: {self.value}"

    def codegen(self, module, builder):
        return builder.ret(self.value.codegen(module, builder))

@dataclass
class IdOrNum:
    value: Union[str, int]

    def __str__(self, level=0):
        return str(self.value)

    def codegen(self, module, builder):
        if isinstance(self.value, int):
            return ir.Constant(ir.IntType(32), self.value)
        else:
            ptr = module.globals.get(self.value)
            if ptr is None:
                raise Exception(f"Undefined variable: {self.value}")
            return builder.load(ptr)

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

    def codegen(self, module, builder):
        left_val = self.left.codegen(module, builder)
        right_val = self.right.codegen(module, builder)
        if isinstance(self.operator, LogicOp):
            if self.operator.operator == '<':
                return builder.icmp_signed('<', left_val, right_val)
            elif self.operator.operator == '>':
                return builder.icmp_signed('>', left_val, right_val)
            elif self.operator.operator == '==':
                return builder.icmp_signed('==', left_val, right_val)
            elif self.operator.operator == '>=':
                return builder.icmp_signed('>=', left_val, right_val)
            elif self.operator.operator == '<=':
                return builder.icmp_signed('<=', left_val, right_val)
        elif isinstance(self.operator, ArithmOp):
            if self.operator.operator == '+':
                return builder.add(left_val, right_val)
            elif self.operator.operator == '-':
                return builder.sub(left_val, right_val)
            elif self.operator.operator == '*':
                return builder.mul(left_val, right_val)
            elif self.operator.operator == '/':
                return builder.sdiv(left_val, right_val)
            if self.comparison:
                comparison_val = self.comparison.codegen(module, builder)
                return builder.icmp_signed('==', left_val, comparison_val)

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
