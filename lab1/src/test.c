#include <stdio.h>
#include <stdlib.h>

int sum(int a, int b) {
    int res;
    res = a + b;
    return res;
}

int main() {
    int n = 3;
    int *arr = NULL;
    arr = (int*)malloc(n);
    int a = 5;
    int b = 1;
    int c = 6;

    if (rand() > 0) {
        a += b;
    } else {
        a -= c;
    }
    printf("%d, %d, sum:%d", a, b, sum(a,b));
    arr[0] = sum(a,b);
    int z = arr[0];
    printf("%d", z);
    free(arr);
    return 0;
}

// gcc -fdump-tree-ssa-graph src/test.c
// dot -Tpng a-test.c.021t.ssa.dot > output.png