import networkx as nx
import json

def read_raw_function(filepath):
    with open(filepath, 'r') as f:
        return f.readlines()

def generate_code(file_filepath, myslice_filepath):
    file_code_list = read_raw_function(file_filepath)
    slice_codes_dict = {}
    slice_codes = []
    G = nx.drawing.nx_agraph.read_dot(myslice_filepath)
    for node in G.nodes(data=True):
        node_location = node[1].get('location')
        node_location_index = int(node_location) - 1
        node_file_code = file_code_list[node_location_index]
        if node_location not in slice_codes_dict:
            slice_codes_dict[node_location] = node_file_code

    slice_codes_dict = dict(sorted(slice_codes_dict.items(), key=lambda x: x[0]))
    slice_codes = list(slice_codes_dict.values())

    codes_dict_save_filepath = myslice_filepath.replace('.dot', '_code.json')
    with open(codes_dict_save_filepath, 'w') as f:
        f.write(json.dumps(slice_codes_dict, indent=4))
    slice_codes_save_filepath = myslice_filepath.replace('.dot', '_code.c')
    with open(slice_codes_save_filepath, 'w') as f:
        f.writelines(slice_codes)
    
    print(codes_dict_save_filepath)
    print(slice_codes_save_filepath)


def test():
    file_filepath = "my-everthing/data/code/file_code_old-97bf6f81_145.c"
    myslice_filepath = "tmp_slice.dot"
    generate_code(file_filepath, myslice_filepath)


if __name__=="__main__":
    test()

