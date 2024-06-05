from llvmlite import ir

class LLVMGenerator:
    def __init__(self):
        self.module = ir.Module(name="simple_module")
        self.builder = None
        self.func = None
        self.block = None
        self.variables = {}

    def generate(self, node):
        func_type = ir.FunctionType(ir.IntType(32), [])
        self.func = ir.Function(self.module, func_type, name="main")
        block = self.func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        self.visit(node)
        self.builder.ret(self.variables['d'])

    def visit(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.visit(stmt)
        elif isinstance(node, Assignment):
            value = self.visit(node.value)
            var = self.builder.alloca(ir.IntType(32), name=node.name)
            self.builder.store(value, var)
            self.variables[node.name] = var
        elif isinstance(node, BinaryOperation):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if node.operator == '+':
                return self.builder.add(left, right)
            elif node.operator == '-':
                return self.builder.sub(left, right)
            elif node.operator == '*':
                return self.builder.mul(left, right)
            elif node.operator == '/':
                return self.builder.sdiv(left, right)
        elif isinstance(node, IfStatement):
            condition = self.visit(node.condition)
            true_block = self.func.append_basic_block("if_true")
            false_block = self.func.append_basic_block("if_false")
            merge_block = self.func.append_basic_block("if_merge")

            self.builder.cbranch(condition, true_block, false_block)

            self.builder.position_at_end(true_block)
            for stmt in node.true_block:
                self.visit(stmt)
            self.builder.branch(merge_block)

            self.builder.position_at_end(false_block)
            for stmt in node.false_block:
                self.visit(stmt)
            self.builder.branch(merge_block)

            self.builder.position_at_end(merge_block)
        elif isinstance(node, ForStatement):
            self.visit(node.init)
            loop_cond_block = self.func.append_basic_block("loop_cond")
            loop_body_block = self.func.append_basic_block("loop_body")
            after_loop_block = self.func.append_basic_block("after_loop")

            self.builder.branch(loop_cond_block)
            self.builder.position_at_end(loop_cond_block)
            condition = self.visit(node.condition)
            self.builder.cbranch(condition, loop_body_block, after_loop_block)

            self.builder.position_at_end(loop_body_block)
            for stmt in node.body:
                self.visit(stmt)
            self.visit(node.increment)
            self.builder.branch(loop_cond_block)

            self.builder.position_at_end(after_loop_block)
        elif isinstance(node, ReturnStatement):
            return self.visit(node.value)
        elif isinstance(node, int):
            return ir.Constant(ir.IntType(32), node)
        elif isinstance(node, str):
            return self.builder.load(self.variables[node])
        else:
            raise ValueError(f"Unknown AST node: {node}")

# Example usage
llvm_gen = LLVMGenerator()
llvm_gen.generate(ast)
print(llvm_gen.module)
