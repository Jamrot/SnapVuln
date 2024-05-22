#include <stdio.h>
#include <string.h>

int generateRandomNumber() {
    return rand() % 100;
}

void printMessage() {
    printf("This is a message from a harmless function.\n");
}

void vulnerableFunction(char *input) {
    char buffer[50];
    int a=1;
        strcpy(buffer, input);

    printf("Buffer content: %s\n", buffer);
}

int main() {
    char userInput[100];

        printMessage();
    printf("Random number: %d\n", generateRandomNumber());

        printf("Enter some text: ");
    fgets(userInput, sizeof(userInput), stdin);

        userInput[strcspn(userInput, "\n")] = 0;

        vulnerableFunction(userInput);

        printf("Random number: %d\n", generateRandomNumber());
    printMessage();

    return 0;
}
