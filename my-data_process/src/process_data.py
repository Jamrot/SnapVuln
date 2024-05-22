import os
from tqdm import tqdm
import glob
import json
from slice_rules import *

def read_raw_function(file_path):
	with open(file_path, 'r', encoding='utf-8') as f:
		txt = f.read()
	return txt


def convert_nodes_edges(dot, mode='default'):
    new_nodes, new_edges = [], []
    if mode == 'default':
        nodes, edges = get_nodes_and_edges(dot, mode)
    elif mode == 'string':
        nodes = dot['nodes']
        edges = dot['edges']
    else:
        return None, None

    node_ids = sorted([int(node['ID']) for node in nodes])
    for node in nodes:
        # node['ID'] = node_ids.index(int(node['ID']))
        new_nodes.append(node)

    for edge in edges:
        # new_edges.append([edge['type'], node_ids.index(int(edge['front'])), node_ids.index(int(edge['rear']))])
        new_edges.append([edge['type'], edge['front'], edge['rear']])

    return new_nodes, new_edges


def get_slices(dotfile):
    bo_slices, ml_slices, io_slices, np_slices, uaf_slices, df_slices = [], [], [], [], [], []

    nodes, edges = get_nodes_and_edges(dotfile)
    slice_set = bo_slice(nodes, edges)
    for _slice in slice_set:
        ns, es = convert_nodes_edges(_slice, 'string')
        # flag = 1
        # for s in bo_slices:
        # 	tmp = [i for i in ns if i not in s['nodes']]
        # 	if len(tmp)==0:
        # 		print("The slice belongs to another slice.")
        # 		flag = 0
        # if flag:
        content = {'criterion': _slice['criterion'],'nodes': ns, 'edges': es}
        bo_slices.append(content)

    slice_set = ml_slice(nodes, edges)
    for _slice in slice_set:
        ns, es = convert_nodes_edges(_slice, 'string')
        # flag = 1
        # for s in ml_slices:
        # 	tmp = [i for i in ns if i not in s['nodes']]
        # 	if len(tmp)==0:
        # 		print("The slice belongs to another slice.")
        # 		flag = 0
        # if flag:
        content = {'criterion': _slice['criterion'],'nodes': ns, 'edges': es}
        ml_slices.append(content)

    slice_set = io_slice(nodes, edges)
    io_slices = []
    for _slice in slice_set:
        ns, es = convert_nodes_edges(_slice, 'string')
        # flag = 1
        # for s in io_slices:
        # 	tmp = [i for i in ns if i not in s['nodes']]
        # 	if len(tmp)==0:
        # 		print("The slice belongs to another slice.")
        # 		flag = 0
        # if flag:
        content = {'criterion': _slice['criterion'],'nodes': ns, 'edges': es}
        io_slices.append(content)

    slice_set = np_slice(nodes, edges)
    np_slices = []
    for _slice in slice_set:
        ns, es = convert_nodes_edges(_slice, 'string')
        # flag = 1
        # for s in np_slices:
        # 	tmp = [i for i in ns if i not in s['nodes']]
        # 	if len(tmp)==0:
        # 		print("The slice belongs to another slice.")
        # 		flag = 0
        # if flag:
        content = {'criterion': _slice['criterion'],'nodes': ns, 'edges': es}
        np_slices.append(content)

    slice_set = uaf_slice(nodes, edges)
    uaf_slices = []
    for _slice in slice_set:
        ns, es = convert_nodes_edges(_slice, 'string')
        # flag = 1
        # for s in uaf_slices:
        # 	tmp = [i for i in ns if i not in s['nodes']]
        # 	if len(tmp)==0:
        # 		print("The slice belongs to another slice.")
        # 		flag = 0
        # if flag:
        content = {'criterion': _slice['criterion'],'nodes': ns, 'edges': es}
        uaf_slices.append(content)

    slice_set = df_slice(nodes, edges)
    df_slices = []
    for _slice in slice_set:
        ns, es = convert_nodes_edges(_slice, 'string')
        # flag = 1
        # for s in df_slices:
        # 	tmp = [i for i in ns if i not in s['nodes']]
        # 	if len(tmp)==0:
        # 		print("The slice belongs to another slice.")
        # 		flag = 0
        # if flag:
        content = {'criterion': _slice['criterion'],'nodes': ns, 'edges': es}
        df_slices.append(content)

    if len(bo_slices) + len(ml_slices) + len(io_slices) + len(np_slices) + len(uaf_slices) + len(df_slices) == 0:
        return None, None, None, None, None

    return bo_slices, ml_slices, io_slices, np_slices, uaf_slices, df_slices


def single_instance_process(file_filename, multi_func_folder, multi_dot_folder, single_func_folder, single_dot_folder, output_folder, label):
    """
    Parameters:
        file_filename: str, filename in multi_func_folder(???)
        multi_func_folder: str, path to {dataset}/func/{label}/multi folder
        multi_dot_folder: str, path to {dataset}/dot/{label}/combine folder (interprocedural dot graph)
        single_func_folder: str, path to {dataset}/func/{label}/single folder
        single_dot_folder: str, path to {dataset}/dot/{label}/single/dots folder
    
    Local Variables:
        target: int, 1 if label is vuln, 0 if label is nonvuln
        bug_func_filename: str, filename of single_func
        bug_dot_filepath: str, path to single_dot file
        file_dot_filepath: str, path to comnbine_dot (multi_dot, interprocedural dot graph) file

    """
    bug_func_filename = file_filename.replace("-multi_function.c", "-bug_function.c")
    file_dot_filename = file_filename.replace(".c",".dot")
    bug_dot_filename = bug_func_filename.replace(".c","*.c.dot")

    # find bug_func filepath
    if bug_func_filename not in os.listdir(single_func_folder):
        print("No bug function.")
        return None
    else:
        bug_func_filepath = os.path.join(single_func_folder,bug_func_filename)

    # find combine_dots filepath (interprocedural dot graph)
    if file_dot_filename not in os.listdir(multi_dot_folder):
        print("No multi-function dot.")
        return None
    else:
        file_dot_filepath = os.path.join(multi_dot_folder, file_dot_filename)
	
    # find single_dots filepath
    single_dots = glob.glob(os.path.join(single_dot_folder,bug_dot_filename))
    if len(single_dots) == 0:
        print("No bug dot.")
        return None
    else:
        bug_dot_filepath = single_dots[0]
        
    if label == "vuln":
        target = 1 
        if "BUFFER_OVERRUN" in file_filename or "Buffer_Overflow" in file_filename:
            vul_type = "buffer_overflow"
        elif "INTEGER_OVERFLOW" in file_filename or "Integer_Overflow" in file_filename:
            vul_type = "integer_overflow"
        elif "NULLPTR_DEREFERENCE" in file_filename or "NULL_Pointer_Dereference" in file_filename:
            vul_type = "null_pointers"
        elif "Memory_Leak" in file_filename:
            vul_type = "memory_leak"
        elif "Double_Free" in file_filename:
            vul_type = "double_free"
        elif "Use_After_Free" in file_filename:
            vul_type = "use_after_free"
        else:
            vul_type = "unknown"
    else:
        target = 0
        vul_type = "nonvuln"
    
    # TODO: generate bug_txt, bug_tokens
    bug_txt = read_raw_function(bug_func_filepath)
    # if len(bug_txt.split('\n')) >= 1500:
    #     print("file too big.")
    #     return None
    bug_tokens = tokenizer(bug_txt)
    bug_dot_nodes, bug_dot_edges = convert_nodes_edges(bug_dot_filepath)
    # bo_slices, ml_slices, io_slices, np_slices, uaf_slices, df_slices = get_slices(bug_dot_filepath)

    file_filepath = os.path.join(multi_func_folder,file_filename)
    file_txt = read_raw_function(file_filepath)
    # if len(file_txt.split('\n')) >= 1500:
    # 	print("file too big.")
    # 	return None
    file_tokens = tokenizer(file_txt)
    file_dot_nodes, file_dot_edges = convert_nodes_edges(file_dot_filepath)

    bo_slices, ml_slices, io_slices, np_slices, uaf_slices, df_slices = get_slices(file_dot_filepath)
    if bo_slices == None:
        print("No slices")
        return None
    
    my_sample = {'bo_slices':bo_slices, 'ml_slices':ml_slices, 'io_slices':io_slices, 'np_slices':np_slices, 'uaf_slices':uaf_slices, 'df_slices':df_slices,
                    'file_txt':file_txt, 'file_tokens':file_tokens, 'file':file_filepath,'vul_type':vul_type,'target': int(target)}

    multi_sample = {'multi_graph': {'nodes': file_dot_nodes, 'edges': file_dot_edges},
                    'file_txt':file_txt, 'file_tokens':file_tokens,'file':file_filepath,'vul_type':vul_type,'target': int(target)}

    single_sample = {'single_graph':{'nodes': bug_dot_nodes, 'edges': bug_dot_edges}, 
                        'bug_txt':bug_txt, 'bug_tokens':bug_tokens, 'bug_func':bug_func_filepath,'file':file_filepath,'vul_type':vul_type,'target': int(target)}	

    # myfile = os.path.join(output_folder,label+"_my.jsonl")
    # multi_file = os.path.join(output_folder,label+"_multi.jsonl")
    # single_file = os.path.join(output_folder,label+"_single.jsonl")

    # with open(myfile, "a") as f:
    #     f.write(json.dumps(my_sample)+'\n')
    # with open(multi_file, "a") as f:
    #     f.write(json.dumps(multi_sample)+'\n')
    # with open(single_file, "a") as f:
    #     f.write(json.dumps(single_sample)+'\n')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    myfile = os.path.join(output_folder,label+"_my.json")
    multi_file = os.path.join(output_folder,label+"_multi.json")
    single_file = os.path.join(output_folder,label+"_single.json")

    with open(myfile, "w") as f:
        json.dump(my_sample, f)
    with open(multi_file, "w") as f:
        json.dump(multi_sample, f)
    with open(single_file, "w") as f:
        json.dump(single_sample, f)

    print("output files: ", myfile, multi_file, single_file)

def main():
    filepath = "my-data_process/data_test/bo-test/func/vuln/multi/my-BUFFER_OVERFLOW-multi_function.c"
    file = os.path.basename(filepath)
    multi_func_folder = "my-data_process/data_test/bo-test/func/vuln/multi"
    multi_dot_folder = "my-data_process/data_test/bo-test/dot/vuln/combine"
    single_func_folder = "my-data_process/data_test/bo-test/func/vuln/single"
    single_dot_folder = "my-data_process/data_test/bo-test/dot/vuln/single"
    output_folder = "my-data_process/data_test/bo-test/output"
    label = ""
    single_instance_process(
         file_filename=file,
         multi_func_folder=multi_func_folder,
         multi_dot_folder=multi_dot_folder,
         single_func_folder=single_func_folder,
         single_dot_folder=single_dot_folder,
         output_folder=output_folder,
         label=label
         )

if __name__=="__main__":
    main()
    # file = "openssl-ff59ce71b50dbd735a065cb2a832ad870593845f_1-auto_labeler-INTEGER_OVERFLOW_L5-multi_function.c"
    # single_func_folder = "my-data_process/data_test/d2a/func/vuln/single"
    # single_dot_folder = "my-data_process/data_test/d2a/dot/vuln/single"
    # multi_func_folder = "my-data_process/data_test/d2a/func/vuln/multi"
    # multi_dot_folder = "my-data_process/data_test/d2a/dot/vuln/combine"
    # output_folder = ""
    # label = ""
    # single_instance_process(
    #      file_filename=file,
    #      multi_func_folder=multi_func_folder,
    #      multi_dot_folder=multi_dot_folder,
    #      single_func_folder=single_func_folder,
    #      single_dot_folder=single_dot_folder,
    #      output_folder=output_folder,
    #      label=label
    #      )