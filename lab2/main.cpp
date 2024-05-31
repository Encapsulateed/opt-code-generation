#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/Verifier.h>
#include <llvm/Support/raw_ostream.h>

int main() {
    // Создаем контекст и модуль
    llvm::LLVMContext Context;
    std::unique_ptr<llvm::Module> Module = std::make_unique<llvm::Module>("main_module", Context);

    // Создаем функцию main
    llvm::FunctionType *FuncType = llvm::FunctionType::get(llvm::Type::getInt32Ty(Context), false);
    llvm::Function *MainFunc = llvm::Function::Create(FuncType, llvm::Function::ExternalLinkage, "main", Module.get());

    // Создаем основной блок функции main
    llvm::BasicBlock *EntryBB = llvm::BasicBlock::Create(Context, "entry", MainFunc);
    llvm::IRBuilder<> Builder(EntryBB);

    // Создаем константы 353 и 48
    llvm::Value *Const353 = llvm::ConstantInt::get(llvm::Type::getInt32Ty(Context), 353);
    llvm::Value *Const48 = llvm::ConstantInt::get(llvm::Type::getInt32Ty(Context), 48);

    // Складываем константы
    llvm::Value *Add = Builder.CreateAdd(Const353, Const48, "addtmp");

    // Возвращаем результат сложения
    Builder.CreateRet(Add);

    // Проверяем корректность IR-кода
    llvm::verifyFunction(*MainFunc);

    // Выводим LLVM IR-код в консоль
    Module->print(llvm::outs(), nullptr);

    return 0;
}
