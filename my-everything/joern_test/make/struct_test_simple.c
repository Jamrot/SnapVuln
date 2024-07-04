#include <stdio.h>

struct struct_a {
    int struct_A_int[10];
};

struct struct_b {
    struct struct_a struct_B_A;
};

struct struct_c {
    union {
        struct struct_b struct_C_B;
    };
};

int handle_preamble(struct struct_c *c_real) {
    struct struct_a *a_real = &c_real->struct_C_B.struct_B_A;
    a_real->struct_A_int[0] = 25;

    int ctrl_len = c_real->struct_C_B.struct_B_A.struct_A_int[0];

    printf("ctrl_len: %d\n", ctrl_len);
    
    return 0;
}

int main() {
    struct struct_c c_real;
    handle_preamble(&c_real);
    return 0;
}