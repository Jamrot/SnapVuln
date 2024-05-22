import os
import json

def read_raw_function(filepath):
    with open(filepath, 'r') as f:
        return f.readlines()

def generate_code(file_filepath, myslice_filepath):
    file_code_list = read_raw_function(file_filepath)
    myslices = {}
    with open(myslice_filepath, 'r') as f:
        myslices = json.load(f)
    
    myslice_code_dict = {}
    for slice_type in myslices:
        if 'slice' not in slice_type:
            continue
        slice_list = myslices[slice_type]
        slice_type_code = []
        for single_slice in slice_list:
            slice_codes = {}
            slice_nodes = single_slice['nodes']
            slice_edges = single_slice['edges']
            slice_criterion = single_slice['criterion'] if 'criterion' in single_slice else None            
            for node in slice_nodes:
                # node_id = node['ID']
                # node_type = node['type']
                # node_name = node['name']
                # node_code = node['code']
                node_location = int(node['location']) if 'location' in node else None
                if not node_location:
                    continue
                node_location_index = node_location - 1
                node_file_code = file_code_list[node_location_index]
                # print(node_file_code)
                if node_location not in slice_codes:
                    slice_codes[node_location] = node_file_code
            # sort slice codes by line number
            slice_codes = dict(sorted(slice_codes.items(), key=lambda x: x[0]))
            slice_codes['criterion'] = slice_criterion
            slice_type_code.append(slice_codes)
        myslice_code_dict[slice_type] = slice_type_code
    
    return myslice_code_dict

def generate_slice_codes():
    file_filepath = "my-data_process/data_test/bo-test/func/vuln/multi/my-BUFFER_OVERFLOW-multi_function.c"
    myslice_filepath = "my-data_process/data_test/bo-test/output/_my.json"
    myslice_code_dict = generate_code(file_filepath, myslice_filepath)
    output_filepath = myslice_filepath.replace('.json', '_code.json')
    print(output_filepath)
    with open(output_filepath, 'w') as f:
        json.dump(myslice_code_dict, f)

if __name__=="__main__":
    generate_slice_codes()