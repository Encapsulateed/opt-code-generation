from dataclasses import dataclass, field
from typing import List, Optional, Union, Iterator
import llvmlite.ir as ir

# Класс Program представляет собой программу, состоящую из набора инструкций.
@dataclass
class Program:
    statements: 'Statements'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Program:\n" + self.statements.__str__(level + 1)

    # Генерация LLVM IR кода для всей программы.
    def codegen(self, module, builder):
        self.statements.codegen(module, builder)

# Класс Statements представляет список инструкций.
@dataclass
class Statements:
    statements: List['Statement']

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Statements:\n" + '\n'.join(s.__str__(level + 1) for s in self.statements)

    def __iter__(self) -> Iterator['Statement']:
        return iter(self.statements)

    # Генерация LLVM IR кода для каждой инструкции в списке.
    def codegen(self, module, builder):
        for statement in self.statements:
            statement.codegen(module, builder)

# Класс Statement представляет одну инструкцию (например, присваивание, if, for, return).
@dataclass
class Statement:
    statement: Union['Assignment', 'IfStatement', 'ForStatement', 'ReturnStatement']

    def __str__(self, level=0):
        return self.statement.__str__(level)

    # Генерация LLVM IR кода для конкретной инструкции.
    def codegen(self, module, builder):
        self.statement.codegen(module, builder)

# Класс Assignment представляет операцию присваивания (например, x = 2).
@dataclass
class Assignment:
    ident: str
    value: 'IdOrNum'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}Assignment: {self.ident} = {self.value}"

    # Генерация LLVM IR кода для присваивания.
    def codegen(self, module, builder):
        value = self.value.codegen(module, builder)
        # Выделение памяти для переменной.
        ptr = builder.alloca(value.type, name=self.ident)
        # Сохранение значения в выделенную память.
        builder.store(value, ptr)
        # Сохранение указателя на переменную в глобальной области видимости модуля.
        module.globals[self.ident] = ptr  
        return ptr

# Класс IfStatement представляет условную конструкцию (if).
@dataclass
class IfStatement:
    expr: 'Expr'
    statements: Statements

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return (f"{indent}IfStatement:\n"
                f"{self.expr.__str__(level + 1)}\n"
                f"{self.statements.__str__(level + 1)}")

    # Генерация LLVM IR кода для условной конструкции if.
    def codegen(self, module, builder):
        cond = self.expr.codegen(module, builder)
        then_block = builder.function.append_basic_block(name="then")
        merge_block = builder.function.append_basic_block(name="ifcont")

        # Условное ветвление на основе значения cond.
        builder.cbranch(cond, then_block, merge_block)

        # Генерация кода для блока then.
        builder.position_at_end(then_block)
        self.statements.codegen(module, builder)
        if not builder.block.is_terminated:
            builder.branch(merge_block)

        # Завершение генерации кода для if-конструкции.
        builder.position_at_end(merge_block)

# Класс ForStatement представляет цикл for.
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

    # Генерация LLVM IR кода для цикла for.
    def codegen(self, module, builder):
        self.assignment.codegen(module, builder)
        loop_block = builder.function.append_basic_block(name="loop")
        after_block = builder.function.append_basic_block(name="afterloop")

        # Переход к блоку loop.
        builder.branch(loop_block)
        builder.position_at_end(loop_block)

        # Генерация кода для условия и тела цикла.
        cond = self.expr1.codegen(module, builder)
        with builder.if_then(cond):
            self.statements.codegen(module, builder)
            self.expr2.codegen(module, builder)
            if not builder.block.is_terminated:
                builder.branch(loop_block)

        # Завершение генерации кода для цикла for.
        if not builder.block.is_terminated:
            builder.branch(after_block)

        builder.position_at_end(after_block)

# Класс ReturnStatement представляет операцию возврата значения (return).
@dataclass
class ReturnStatement:
    value: 'IdOrNum'

    def __str__(self, level=0):
        indent = ' ' * (level * 2)
        return f"{indent}ReturnStatement: {self.value}"

    # Генерация LLVM IR кода для возврата значения.
    def codegen(self, module, builder):
        return builder.ret(self.value.codegen(module, builder))

# Класс IdOrNum представляет либо идентификатор переменной, либо числовое значение.
@dataclass
class IdOrNum:
    value: Union[str, int]

    def __str__(self, level=0):
        return str(self.value)

    # Генерация LLVM IR кода для идентификатора или числового значения.
    def codegen(self, module, builder):
        if isinstance(self.value, int):
            # Генерация кода для числового значения.
            return ir.Constant(ir.IntType(32), self.value)
        else:
            # Генерация кода для идентификатора переменной.
            ptr = module.globals.get(self.value)
            if ptr is None:
                raise Exception(f"Undefined variable: {self.value}")
            return builder.load(ptr)

# Класс Expr представляет выражение, состоящее из двух операндов и оператора.
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

    # Генерация LLVM IR кода для выражения.
    def codegen(self, module, builder):
        left_val = self.left.codegen(module, builder)
        right_val = self.right.codegen(module, builder)
        if isinstance(self.operator, LogicOp):
            # Генерация кода для логических операций.
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
            # Генерация кода для арифметических операций.
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

# Класс LogicOp представляет логический оператор (например, <, >, ==).
@dataclass
class LogicOp:
    operator: str

    def __str__(self, level=0):
        return self.operator

# Класс ArithmOp представляет арифметический оператор (например, +, -, *, /).
@dataclass
class ArithmOp:
    operator: str

    def __str__(self, level=0):
        return self.operator
