#include <stdio.h>

void example_function(int x) {
    int a = 0;
    int b = 1;
    int c;

    if (x > 0) {
        a = 2;
    } else {
        b = 3;
    }

    c = a + b;
    printf("Result: %d\n", c);
}

int main() {
    example_function(5);
    return 0;
}
