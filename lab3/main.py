def main():
    with open('input.txt', 'r') as file:
        source_code = file.read()

    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    llvm_gen = LLVMGenerator()
    llvm_gen.generate(ast)

    print(llvm_gen.module)

if __name__ == "__main__":
    main()
