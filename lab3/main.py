from lexer import Lexer
from parse import Parser
import llvmlite.ir as ir
import llvmlite.binding as llvm
import sys
import traceback

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <filename>")
        return

    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    lexer = Lexer(code)
    parser = Parser(lexer)
    try:
        program = parser.parse()
        print(program)

        # Code generation
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        
        module = ir.Module(name=filename)
        func_type = ir.FunctionType(ir.VoidType(), [])
        func = ir.Function(module, func_type, name='main')
        block = func.append_basic_block(name='entry')
        builder = ir.IRBuilder(block)
        
        # Передаем функцию и builder в codegen
        program.codegen(module, builder)
        
       # builder.ret_void()
        print(module)
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
