import os

dir = "my-everthing/src/slicing"

def sum_linenum(dir):
    sum = 0
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), 'r') as f:
                    sum += len(f.readlines())
    return sum

print(sum_linenum(dir))