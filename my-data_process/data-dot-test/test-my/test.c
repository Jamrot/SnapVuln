#include <stdio.h> // file 节点，引用标准库文件
#include <stdlib.h> // file 节点，引用标准库文件

// metaData 节点
// typeDecl 节点
typedef struct {
    int id; // member 节点
    char name[50]; // member 节点
    int age; // member 节点
} Person;

// method 节点
void printPersonInfo(Person p) {
    // local 节点
    char info[100]; // identifier 节点
    // literal 节点
    sprintf(info, "ID: %d, Name: %s, Age: %d", p.id, p.name, p.age); // call 节点, identifier 节点, literal 节点
    printf("%s\n", info); // call 节点, identifier 节点, literal 节点
}

// method 节点
Person createPerson(int id, const char* name, int age) {
    // local 节点
    Person p; // identifier 节点
    p.id = id; // identifier 节点, literal 节点
    p.age = age; // identifier 节点, literal 节点
    // call 节点
    snprintf(p.name, sizeof(p.name), "%s", name); // identifier 节点, literal 节点
    // methodReturn 节点
    return p; // return 节点
}

int main() { // method 节点
    // local 节点
    Person person1 = createPerson(1, "Alice", 30); // call 节点, identifier 节点, literal 节点
    // call 节点
    printPersonInfo(person1); // identifier 节点
    // operator 节点
    int doubledAge = person1.age * 2; // identifier 节点, operator 节点, literal 节点
    // call 节点
    printf("Doubled Age: %d\n", doubledAge); // identifier 节点, literal 节点
    // call 节点
    return 0; // methodReturn 节点, literal 节点
}
