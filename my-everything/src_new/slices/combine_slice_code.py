import json
import re

def extract_line_number(line):
    # 使用正则表达式提取行号
    match = re.match(r'L(\d+)', line)
    if match:
        return int(match.group(1))
    else:
        return float('inf')  # 如果没有匹配，返回一个极大值，这样不会影响排序

def combine_slice_code_json(json_filepath_list):
    all_slice_json_dict = {}
    for json_filepath in json_filepath_list:
        with open(json_filepath, 'r') as f:
            all_slice_json_dict[json_filepath] = json.load(f)

    combined_slice_dict = {"files": []}
    file_func_map = {}

    for json_filepath, slice_dict in all_slice_json_dict.items():
        files = slice_dict['files']
        for file in files:
            filename = file['file_name']
            if filename not in file_func_map:
                file_func_map[filename] = {}

            functions = file['functions']
            for func in functions:
                funcname = func['function_name']
                if funcname not in file_func_map[filename]:
                    file_func_map[filename][funcname] = {
                        'new_lines': set(),
                        'old_lines': set(),
                        'both_lines': set()
                    }  # 使用 set 避免重复

                new_lines = func.get('new_lines', [])
                old_lines = func.get('old_lines', [])
                both_lines = func.get('both_lines', [])

                file_func_map[filename][funcname]['new_lines'].update(new_lines)
                file_func_map[filename][funcname]['old_lines'].update(old_lines)
                file_func_map[filename][funcname]['both_lines'].update(both_lines)

    for filename, funcs in file_func_map.items():
        file_entry = {
            "file_name": filename,
            "functions": []
        }
        for funcname, lines_dict in funcs.items():
            func_entry = {
                "function_name": funcname,
                "new_lines": sorted(lines_dict['new_lines'], key=extract_line_number),
                "old_lines": sorted(lines_dict['old_lines'], key=extract_line_number),
                "both_lines": sorted(lines_dict['both_lines'], key=extract_line_number)
            }
            file_entry["functions"].append(func_entry)
        combined_slice_dict["files"].append(file_entry)

    return combined_slice_dict

json_filepath_list = [
    "my-everything/data/test_slice/response/a282a2f/collate.slice/slice-collate-a282a2f-file.slice_code.json",
    "my-everything/data/test_slice/response/a282a2f/collate.slice/slice-collate-a282a2f-function.slice_code.json"]

combined_slice_dict = combine_slice_code_json(json_filepath_list)

with open("test.json", 'w') as f:
    json.dump(combined_slice_dict, f, indent=2)