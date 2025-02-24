import os

dir = "my-everything/src_new"

def sum_linenum(dir):
    sum = 0
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)        
                with open(filepath, 'r') as f:
                    file_linenum = len(f.readlines())
                if file_linenum > 0:
                    print(f"{filepath}: {file_linenum}")
                sum += file_linenum
    return sum

print(sum_linenum(dir))