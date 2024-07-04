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

int main() {
    struct struct_c c_real;

    struct struct_a *a_real = &c_real->struct_C_B.struct_B_A; // handle_preamble(&c_real);

    a_real->struct_A_int[0] = 0; // source, decode_preamble(a_real)

    int ctrl_len = c_real->struct_C_B.struct_B_A.struct_A_int[0]; // prepare_read_control(c_real) 
    
    return 0;
}