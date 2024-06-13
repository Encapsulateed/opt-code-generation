from llvmlite import ir

# Создание модуля
module = ir.Module(name="simple_module")

# Указание целевого тройного и макета данных
module.triple = "none"
module.data_layout = "none"

func_type = ir.FunctionType(ir.IntType(32), [])
main_func = ir.Function(module, func_type, name="main")

block = main_func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)

result = builder.add(ir.Constant(ir.IntType(32), 353), ir.Constant(ir.IntType(32), 48),name="var")

builder.ret(result)

print(module)
