from llvmlite import ir

# Создание модуля
module = ir.Module(name="simple_module")

# Объявление функции main
func_type = ir.FunctionType(ir.IntType(32), [])
main_func = ir.Function(module, func_type, name="main")

# Создание блока входа для функции main
block = main_func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)

# Генерация инструкции для сложения 353 и 48
result = builder.add(ir.Constant(ir.IntType(32), 353), ir.Constant(ir.IntType(32), 48))

# Возвращение результата
builder.ret(result)

# Печать сгенерированного LLVM кода
print(module)
