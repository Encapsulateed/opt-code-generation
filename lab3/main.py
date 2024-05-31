from llvmlite import ir, binding

# Инициализация контекста и модуля
context = ir.Context()
module = ir.Module(name="simple_module", context=context)
builder = None

# Определяем типы
int_type = ir.IntType(32)
func_type = ir.FunctionType(int_type, [])

# Создаем функцию main
main_func = ir.Function(module, func_type, name="main")
entry_block = main_func.append_basic_block(name="entry")
builder = ir.IRBuilder(entry_block)

# Переменные
x = builder.alloca(int_type, name="x")
y = builder.alloca(int_type, name="y")
z = builder.alloca(int_type, name="z")
i = builder.alloca(int_type, name="i")

# Начальные значения
builder.store(ir.Constant(int_type, 5), x)
builder.store(ir.Constant(int_type, 3), y)
builder.store(ir.Constant(int_type, 0), z)

# if (x > y)
x_val = builder.load(x, name="x_val")
y_val = builder.load(y, name="y_val")
cond = builder.icmp_signed('>', x_val, y_val, name="ifcond")

with builder.if_else(cond) as (then, otherwise):
    with then:
        # z = x + y
        sum_val = builder.add(x_val, y_val, name="sum")
        builder.store(sum_val, z)
    with otherwise:
        # z = x * y
        mul_val = builder.mul(x_val, y_val, name="mul")
        builder.store(mul_val, z)

# for (int i = 0; i < 10; i = i + 1)
loop_block = main_func.append_basic_block(name="loop")
after_loop_block = main_func.append_basic_block(name="after_loop")

# i = 0
builder.store(ir.Constant(int_type, 0), i)

# Начало цикла
builder.branch(loop_block)
builder.position_at_end(loop_block)

# Тело цикла
i_val = builder.load(i, name="i_val")
cond = builder.icmp_signed('<', i_val, ir.Constant(int_type, 10), name="loopcond")

with builder.if_else(cond) as (loop, after):
    with loop:
        # z = z + 1
        z_val = builder.load(z, name="z_val")
        new_z_val = builder.add(z_val, ir.Constant(int_type, 1), name="z_plus_1")
        builder.store(new_z_val, z)
        
        # i = i + 1
        new_i_val = builder.add(i_val, ir.Constant(int_type, 1), name="i_plus_1")
        builder.store(new_i_val, i)
        
        # Переход в начало цикла
        builder.branch(loop_block)
    with after:
        # Выход из цикла
        builder.branch(after_loop_block)

builder.position_at_end(after_loop_block)

# return z
ret_val = builder.load(z, name="ret_val")
builder.ret(ret_val)

# Печать сгенерированного LLVM IR
print(module)
