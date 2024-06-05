from lexer import Lexer
from parse import Parser
import sys

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
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
