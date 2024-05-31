Лабораторная #2 
Написать простейший "компилятор" на базе LLVM, который ничего на вход не берёт. Генерирует LLVM код для функции

```
int main()  
{  
     return 353 + 48;  
}
```

# Запуск
```
clang++ `llvm-config --cxxflags --ldflags --libs core` -o main main.cpp
```

```
./main
```