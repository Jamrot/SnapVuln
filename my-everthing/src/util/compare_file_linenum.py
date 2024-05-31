def parse_file(file_path):
    """
    解析文件，返回文件名和行号集合
    :param file_path: 文件路径
    :return: 文件名和行号集合
    """
    file_name = None
    line_numbers = set()

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('file:'):
                file_name = line.split('file:')[1].strip()
            elif ':' in line:
                line_number = line.split(':')[0].strip()
                if line_number.isdigit():
                    line_numbers.add(int(line_number))

    return file_name, line_numbers

def compare_files(file1_path, file2_path):
    """
    比较两个文件是否有相同的行号和文件名
    :param file1_path: 第一个文件路径
    :param file2_path: 第二个文件路径
    :return: 比较结果
    """
    file1_name, file1_lines = parse_file(file1_path)
    file2_name, file2_lines = parse_file(file2_path)

    if file1_name != file2_name:
        print("文件名不同")
        return False

    common_lines = file1_lines.intersection(file2_lines)
    if common_lines:
        print("相同的行号:", common_lines)
        return True
    else:
        print("没有相同的行号")
        return False

# 示例调用
file1_path = 'my-everthing/data/test/0844370f-1/0844370f-tls_strp_read_sock-531/0844370f-tls_strp_read_sock-531.slice/backward/cfg/module/slice-backward_cfg_module-0844370f-tls_strp_read_sock-531.slice_code.slice_code'
file2_path = 'my-everthing/data/test/0844370f/0844370f-tls_strp_read_sock-531/0844370f-tls_strp_read_sock-531.slice/backward/cfg/module/slice-backward_cfg_module-0844370f-tls_strp_read_sock-531.slice_code.slice_code'

result = compare_files(file1_path, file2_path)
if result:
    print("两个文件有相同的行号和文件名")
else:
    print("两个文件没有相同的行号和文件名")
