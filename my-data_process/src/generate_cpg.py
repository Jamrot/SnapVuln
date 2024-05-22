import os
import re
from cpgqls_client import CPGQLSClient, import_code_query
from bash_exe import execute_command, execute_command_err
from build_interprocedural_graph import get_nodes_and_edges
from ctag_func_extractor import get_funcs_in_file
from build_interprocedural_graph import construct_graph


def query_cpg(query, server_endpoint="localhost:8080"):
    server_endpoint = "localhost:8080"
    client = CPGQLSClient(server_endpoint)

    # query = import_code_query("/app/slicing-snapvuln/my-test/data/d2a/func/vuln/single/my-simple-BUFFER_OVERRUN-bug_function.c")    
    result = client.execute(query)
    return result['stdout'], result

def generate_cpg_bash(parse_filepath, out_dir):
    cmd = 'joern-parse %s' % parse_filepath
    res = execute_command(cmd, ".")
    # if not os.path.exists(out_dir):
    #     os.makedirs(out_dir)
    cmd = 'joern-export --repr cpg --out %s' % out_dir
    res = execute_command(cmd, ".")
    print(res)

def generate_cpg(parse_dir, parse_filename, out_dir):
    tmp_dir = 'tmp'
    parse_filepath = os.path.join(parse_dir, parse_filename)
    if not os.path.exists(parse_filepath):
        print("Parse File not found: %s" % parse_filepath)
        exit()
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    # generate cpg_dump
    if os.path.exists(tmp_dir):
        os.system('rm -rf %s' % tmp_dir)
    generate_cpg_bash(parse_filepath, tmp_dir)

    # read func name
    cpg_dir = os.path.join(tmp_dir, parse_filename)
    if not os.path.exists(cpg_dir):
        print("CPG Directory not found: %s" % cpg_dir)
        exit()
    
    func_dot_list = os.listdir(cpg_dir)
    funcname_list = []
    func_path_dict = {}
    for func_dot in func_dot_list:
        if not func_dot.endswith('.dot'):
            continue
        if func_dot == '_global_.dot':
            continue
        funcname = func_dot.replace('.dot', '')
        func_path = os.path.join(cpg_dir, func_dot)
        funcname_list.append(funcname)
        if funcname in func_path_dict:
            print("Duplicate Function Name: %s" % funcname)
            # exit()
        func_path_dict[funcname] = func_path

    # move files in cpg_dump to dataset/dot/vuln/multi
    # rename func_filename to parse_filename.replace('-multi_function.c', '-multi_function_funcname.c.dot')
    for funcname in func_path_dict:
        out_filename = parse_filename.replace('.c', '_%s.c.dot' % funcname)
        out_filepath = os.path.join(out_dir, out_filename)
        func_path = func_path_dict[funcname]
        cmd = 'mv %s %s' % (func_path, out_filepath)
        res = execute_command_err(cmd, ".")

def reconstruct_cpg(cpg_filepath, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_filepath = os.path.join(out_dir, 'reconstruct_' + os.path.basename(cpg_filepath))
    new_cpg_content = 'digraph {\n'

    edge_type_list = ['AST','CALL', 'CDG', 'REACHING_DEF', 'CFG', 'REF'] # remained edge types
    node_label_info = [] # show the node label info
    nodes, edges = get_nodes_and_edges(cpg_filepath)
    for node in nodes:
        node_id = node['ID']
        node_type = node['type'] if 'type' in node else ''
        node_name = node['name'] if 'name' in node else ''
        node_code = node['code'] if 'code' in node else ''
        node_chunk = node['chunk'] if 'chunk' in node else ''

        info_regex = r"\d+ \[.*label=\w+(.*)"
        node_info = re.findall(info_regex, node_chunk, re.S)[0].replace(']', '').strip('\n')

        new_label = '{} [{}]\n {}'.format(node_type, node_name, node_code)
        new_cpg_content += '{} [label="{}"{}]\n'.format(node_id, new_label, node_info)
    
    for edge in edges:
        edge_type = edge['type']
        edge_src = edge['front']
        edge_dst = edge['rear']
        edge_chunk = edge['chunk']

        info_regex = r"\d+ -> \d+ \[.*label=\w+(.*)"
        edge_info = re.findall(info_regex, edge_chunk, re.S)[0].replace(']', '').strip('\n')

        if edge_type in edge_type_list:
            new_cpg_content += '{} -> {} [label="{}"{}]\n'.format(edge_src, edge_dst, edge_type, edge_info)
    
    new_cpg_content += '}'
    with open(out_filepath, 'w') as f:
        f.write(new_cpg_content)


def extract_single_func(file_filepath, func_name, single_func_out_dir = ""):
    file_func_dict = get_funcs_in_file(file_filepath)
    for func_info in file_func_dict:
        if func_info['name'] == func_name:
            # single_func_start = func_info['start']
            # single_func_end = func_info['end']
            single_func_content = func_info['func']
            break
    
    file_filename = os.path.basename(file_filepath)
    if not single_func_out_dir:
        single_func_out_dir = os.path.dirname(file_filepath).replace('multi', 'single')
    if not os.path.exists(single_func_out_dir):
        os.makedirs(single_func_out_dir)

    single_func_filename = file_filename.replace('-multi_function.c', '-bug_function.c')
    single_func_filepath = os.path.join(single_func_out_dir, single_func_filename)

    with open(single_func_filepath, 'w') as f:
        f.write(single_func_content)
    
    return single_func_out_dir, single_func_filename

def build_single_cpg(file_filepath, func_name):
    single_func_dir, single_func_filename = extract_single_func(file_filepath, func_name)
    out_dir = single_func_dir.replace('func', 'dot')
    generate_cpg(parse_dir=single_func_dir, parse_filename=single_func_filename, out_dir=out_dir)

def build_multi_cpg(file_filepath):    
    parse_dir = os.path.dirname(file_filepath)
    parse_filename = os.path.basename(file_filepath)
    out_dir = parse_dir.replace('func', 'dot')
    generate_cpg(
        parse_dir=parse_dir, 
        parse_filename=parse_filename, 
        out_dir=out_dir
    )

def build_combine_cpg(file_filepath):
    file_filename = os.path.basename(file_filepath)
    file_dot_dir = os.path.dirname(file_filepath).replace('func', 'dot')
    out_dir = file_dot_dir.replace('multi', 'combine')
    construct_graph(
        func = file_filename, 
        dot_folder= file_dot_dir,
        out_folder= out_dir
    )



def main():
    file_filepath = 'my-data_process/data_test/bo-test/func/vuln/multi/my-BUFFER_OVERFLOW-multi_function.c'
    build_single_cpg(
        file_filepath = file_filepath, 
        func_name='vulnerableFunction'
    )
    build_multi_cpg(
        file_filepath = file_filepath
    )
    build_combine_cpg(
        file_filepath = file_filepath
    
    )


if __name__=="__main__":
    main()