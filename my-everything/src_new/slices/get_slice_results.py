import os
import re
import json
import networkx as nx
from tqdm import tqdm
from subprocess import Popen, PIPE

from analysis.patch_analyzer import PatchAnalyzer
from analysis.graph_builder import GraphBuilder
from analysis.criterion_extractor import CriterionExtractor
from slices.slicer_new import Slicer
import config.config as config
import utils.get_path as get_path
import api_requests.response_parser as response_parser


import logging
logger = logging.getLogger(__name__)


def read_file(filepath):
    with open(filepath, 'r') as f:
        return f.readlines()


def execute_command(command,cwd):
	try:
		p = Popen(command,stdout=PIPE,stderr=PIPE,cwd=cwd,shell=True)
		content, _ = p.communicate()
		out = content.decode("utf8","ignore")
		return out
	except Exception as e:
		logger.error(f"[Command execution failed] Execution error: {e.stderr}")
		return ''
    

def get_line_map_funcs_in_file(file_path):
    file_func_dict = {}

    cmd2 = 'ctags --fields=+ne-t -o - --sort=no --excmd=number %s' % file_path
    res = execute_command(cmd2, ".")
    if not res:
        with open(file_path, "r", errors="ignore") as rfile:
            file_str = rfile.read()
        if not file_str:
            return file_func_dict
        else:
            logger.error(f"Empty Ctags Result [{file_path}]")
            return file_func_dict
            
    lines = res.splitlines()

    for line in lines:
        fields = line.split()
        if 'f' in fields:            
            start_num = get_num(fields, 'line:')
            end_num = get_num(fields, 'end:')
            func_code = extract_function(file_path, start_num, end_num)
            if start_num is None or end_num is None:
                continue
            for line in range(start_num, end_num + 1):
                if line in file_func_dict:
                    logger.warning(f"Function already exists in file_func_dict: {file_path} {line}")
                    continue

                func_first_line = func_code[0]
                file_func_dict[line] = func_first_line.strip('\n')
            
    return file_func_dict


def get_num(fields, tag):
    for item in fields:
        if tag in item:
            tag_list = item.split(":")
            return int(tag_list[-1])
        

def extract_function(file_path, start_num, end_num):
    with open(file_path, "r", errors="ignore") as rfile:
        lines = rfile.readlines()
        # return "".join(lines[start_num - 1:end_num])
        return lines[start_num - 1:end_num]



def get_slice_info_from_dot_criterion(criterion, myslice_filepath="", level='function', G_slice=None):
    # read code in code filepath list
    code_filepath_list = get_path.get_code_filepath_list_from_criterion(criterion, level=level)
    module_code = {}
    slice_codes_dict = {}
    # get filename and function from each file
    all_filepath = []
    func_line_map_dict = {}
    for file_filepath in code_filepath_list:
        module_code[file_filepath] = read_file(file_filepath)
        slice_codes_dict[file_filepath] = {}
        func_line_map_dict[file_filepath] = get_line_map_funcs_in_file(file_filepath)
        all_filepath.append(file_filepath)

    # get slice graph
    if not G_slice:
        if not os.path.exists(myslice_filepath):
            logger.error(f"[Get slice info failed] Cannot find slice dot file: {myslice_filepath}")
            return None
        else:
            G_slice = nx.drawing.nx_agraph.read_dot(myslice_filepath)
    
    # add node code to slice_codes_dict based on file and location
    for node in G_slice.nodes(data=True):
        node_location = node[1].get('LINE_NUMBER')
        if not node_location:
            logger.warning(f"Cannot find node location: node_id - {node[0]}")
            logger.debug(f"Cannot find node location: node data - {node[1]}")
            continue
        node_location_index = int(node_location) - 1

        # get node filename
        node_filename = node[1].get('filename')
        if not node_filename:
            logger.warning(f"Cannot find node filename: node_id - {node[0]}")
            logger.debug(f"Cannot find node filename: node data - {node[1]}")
            continue

        # get node filepath
        module_dirpath, module_relpath = get_path.get_module_dirpath_from_criterion(criterion)
        node_filepath = os.path.join(module_dirpath, node_filename)
        if node_filepath not in all_filepath:
            logger.warning(f"Invalid node_filepath: {node_filepath}")
            continue
        
        # get node code
        node_file_code = module_code[node_filepath][node_location_index]
        if node_location not in slice_codes_dict[node_filepath]:
            # get node function
            node_func = func_line_map_dict[node_filepath].get(int(node_location), None)
            slice_codes_dict[node_filepath][node_location] = {
                'code': node_file_code,
                'function': node_func
            }

    # sort slice_codes_dict by location
    for file_filepath, file_slice_codes_dict in slice_codes_dict.items():
        slice_codes_dict[file_filepath] = dict(sorted(file_slice_codes_dict.items(), key=lambda x: x[0]))

    all_nodes_list = {node[0]:node[1] for node in G_slice.nodes(data=True)} # node[0]: node id
    all_edges_list = {f"{edge[0]}->{edge[1]}":edge[-1] for edge in G_slice.edges(data=True)}

    slice_info_dict = {
        'code': slice_codes_dict,
        'nodes': all_nodes_list,
        'edges': all_edges_list
    }
    
    codes_dict_save_filepath = myslice_filepath.replace('.dot', '.slice_code.json')
    with open(codes_dict_save_filepath, 'w') as f:
        f.write(json.dumps(slice_info_dict, indent=2))
    
    print(codes_dict_save_filepath)
    return slice_info_dict


def collate_slice_info(slice_info_dict, collate_info_dict):
    # collate_info_dict = {
    #     'code': {},
    #     'nodes': {},
    #     'edges': {}
    # }
    slice_codes_dict = slice_info_dict.get('code')
    slice_nodes_dict = slice_info_dict.get('nodes')
    slice_edges_dict = slice_info_dict.get('edges')

    for file_filepath in slice_codes_dict:
        file_slice_codes_dict = slice_codes_dict[file_filepath]
        if not file_slice_codes_dict:
            continue
        if file_filepath not in collate_info_dict['code']:
            collate_info_dict['code'][file_filepath] = {}
        collate_info_dict['code'][file_filepath].update(file_slice_codes_dict)
    
    for file_filepath, file_slice_codes_dict in collate_info_dict['code'].items():
        collate_info_dict['code'][file_filepath] = dict(sorted(file_slice_codes_dict.items(), key=lambda x: x[0]))
    
    for node, node_data in slice_nodes_dict.items():
        if node not in collate_info_dict['nodes']:
            collate_info_dict['nodes'][node] = node_data
    
    for edge, edge_data in slice_edges_dict.items():
        if edge not in collate_info_dict['edges']:
            collate_info_dict['edges'][edge] = edge_data

    return collate_info_dict


def get_slice_codes_from_info(slice_info_dict, myslice_filepath, commit_id):
    slice_codes_dict = slice_info_dict.get('code')
    save_root = get_path.get_save_root(commit_id=commit_id)

    all_slice_codes = []
    for file_filepath in slice_codes_dict:
        file_slices = slice_codes_dict[file_filepath]
        if not file_slices:
            continue

        # get file relpath
        # TODO: choose print the file_relpath or filename
        file_relpath = os.path.relpath(file_filepath, save_root)
        file_slice_codes = [f"### File: `{file_relpath}`\n\n"]
        

        current_function = None   
        for location in file_slices:
            code = file_slices[location]["code"]
            func_name = file_slices[location]["function"]
            func_str = f"#### Function: `{func_name}`\n\n" if func_name else ""

            if func_str and func_name != current_function:
                if current_function:
                    file_slice_codes.append(f"```\n\n")
                file_slice_codes.append(func_str)
                file_slice_codes.append(f"```c\n")
                current_function = func_name

            file_slice_codes.append(f"L{location}: {code}")
        
        if current_function:
            file_slice_codes.append(f"```\n\n")

        all_slice_codes.extend(file_slice_codes)
    
    slice_codes_save_filepath = myslice_filepath.replace(config.SLICE_DOT_FILE_END, config.SLICE_CODE_FILE_END)
    with open(slice_codes_save_filepath, 'w') as f:
        f.writelines(all_slice_codes)

    print(slice_codes_save_filepath)


def get_slice_codes_json_from_info(slice_info_dict, myslice_filepath, commit_id):
    slice_codes_dict = slice_info_dict.get('code')
    save_root = get_path.get_save_root(commit_id=commit_id)

    all_slice_dict = {"files":[]}
    for file_filepath in slice_codes_dict:
        file_slices = slice_codes_dict[file_filepath]
        if not file_slices:
            continue

        # get file relpath
        # TODO: choose print the file_relpath or filename
        file_relpath = os.path.relpath(file_filepath, save_root)
        file_slice_dict = {
            "file_name":file_relpath,
            "functions":[]}
        

        func_slice_dict = None
        current_func_name = None

        for location in file_slices:
            code = file_slices[location]["code"]
            func_name = file_slices[location]["function"]
            
            if func_name != current_func_name:
                if func_slice_dict:
                    file_slice_dict["functions"].append(func_slice_dict)
                
                current_func_name = func_name
                func_slice_dict = {
                    "function_name": func_name,
                    "lines": [f"L{location}: {code}"]
                }
            else:
                func_slice_dict["lines"].append(f"L{location}: {code}")

        if func_slice_dict:
            file_slice_dict["functions"].append(func_slice_dict)
        
        all_slice_dict['files'].append(file_slice_dict)
    
    slice_codes_save_filepath = myslice_filepath.replace(config.SLICE_DOT_FILE_END, config.SLICE_CODE_FILE_END_JSON)
    with open(slice_codes_save_filepath, 'w') as f:
        json.dump(all_slice_dict, f, indent=2)

    print(slice_codes_save_filepath)


def save_collate_slice_info(collate_info_dict, collate_save_filepath):
    collate_info_filepath = collate_save_filepath.replace(config.SLICE_DOT_FILE_END, config.SLICE_INFO_FILE_END)
    with open(collate_info_filepath, 'w') as f:
        json.dump(collate_info_dict, f, indent=2)
    
    print(collate_info_filepath)