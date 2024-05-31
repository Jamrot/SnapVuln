import os
import re
import json
import networkx as nx
from tqdm import tqdm

from patch_analyzer import PatchAnalyzer
from graph_builder import GraphBuilder
from criterion_extractor import CriterionExtractor
from slicer_new import Slicer
import config

import logging
logger = logging.getLogger(__name__)

import log_config
log_config.setup_logging()



def build_level_graph(code_dir, graph_type="all", level='function', confirm=True, overwrite=False):
    graph_builder = GraphBuilder()
    meta_filepath_list = get_all_meta_filepath(root_dir=code_dir)
    
    for meta_filepath in meta_filepath_list:
        criterion = read_criterion_from_meta(meta_filepath=meta_filepath)
        graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
        parse_path = get_parse_path_from_criterion(criterion=criterion, level=level)
        # check path validation
        if not graph_dir or not parse_path:
            continue
        if not os.path.exists(graph_dir):
            os.makedirs(graph_dir)

        bin_filepath = get_and_check_bin_filepath(criterion=criterion, level=level, confirm=config.BIN_CONFIRM, overwrite=config.BIN_OVERWRITE)
        if config.BIN_OVERWRITE or not os.path.exists(bin_filepath):
            graph_builder.joern_parse(source_path=parse_path, bin_file=bin_filepath)
        
        graph_dump_dir = get_graph_dump_dir(graph_dir=graph_dir, graph_type=graph_type)
        graph_builder.joern_dump_graph(graph_dir=graph_dump_dir, bin_file=bin_filepath, graph_type=graph_type)

        # save_graph_file(graph_dump_dir=graph_dump_dir, criterion=criterion, graph_type=graph_type)
    
    return graph_dir

def get_graph_dump_dir(graph_dir, graph_type):
    graph_dump_dir = os.path.join(graph_dir, "-".join([config.GRAPH_START, graph_type]))
    return graph_dump_dir

def read_criterion_from_meta(meta_filepath):
    with open(meta_filepath, 'r') as f:
        criterion = json.load(f)
    if not len(criterion)==1:
        logger.error(f"Invalid criterion from meta file: {meta_filepath}")
        return None
    criterion = criterion[0]
    return criterion


def get_graph_dir_from_criterion(criterion, level):
    filename_base = criterion.get('save_filename_base')
    save_root = criterion.get('save_root')
    module_path = criterion.get('save_module_dirpath')
    module_dirname = os.path.basename(module_path)
    if level=="module":
        graph_dir = os.path.join(save_root, module_dirname+config.GRAPH_DIR_END)
    else:
        graph_dir = os.path.join(save_root, filename_base, filename_base+config.GRAPH_DIR_END)  
    return graph_dir


def get_parse_path_from_criterion(criterion, level):
    # get module and code filepath
    module_path = criterion.get('save_module_dirpath')
    code_filepath = criterion.get('save_file_code_old_filepath')

    if not os.path.exists(module_path):
        logger.error(f"Module file not found: {module_path}")
        return None
    if not os.path.exists(code_filepath):
        logger.error(f"Code file not found: {code_filepath}")
        return None

    # choose parse path based on level
    if level == "function" or level == "file":
        parse_path = code_filepath
    elif level == "module":
        parse_path = module_path
    else:
        logger.error(f"Invalid parse level: {level}")
        return None
    
    return parse_path


def get_and_check_bin_filepath(criterion, level, confirm=True, overwrite=False):
    graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
    filename_base = criterion.get('save_filename_base')
    module_path = criterion.get('save_module_dirpath')
    module_dirname = os.path.basename(module_path)
    if level=='module':
        bin_filepath = os.path.join(graph_dir, f"{level}-{module_dirname}.bin")
    else:
        bin_filepath = os.path.join(graph_dir, f"{level}-{filename_base}.bin")
    if os.path.exists(bin_filepath):
        if confirm:
            confirm_input = input(f"bin file {bin_filepath} already exists, overwrite? (y/n)")
            overwrite = True if confirm_input=='y' else False
            logger.info(f"bin file overwrite confirm result: {overwrite}")
        if overwrite:
            logger.warning(f"removing bin file: {bin_filepath}")
            os.remove(bin_filepath)
    return bin_filepath


def save_graph_file(graph_dump_dir, criterion, graph_type, level):
    graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
    filename_base = criterion.get('save_filename_base')

    graph_path_dict = get_graph_filepath_from_dump_dir(graph_dump_dir=graph_dump_dir, graph_type=graph_type)
    for codefile_filename, graph_filepath in graph_path_dict.items():
        graph_save_path = os.path.join(graph_dir, "-".join([config.GRAPH_START, graph_type, filename_base, codefile_filename])+config.GRAPH_FILE_END)
        if graph_filepath and os.path.exists(graph_filepath):
            os.system(f"cp {graph_filepath} {graph_save_path}")
            logger.info(f"Graph saved to {graph_save_path}")
        else:
            logger.error(f"Graph file not found: {graph_filepath}")


def get_graph_filepath_from_dump_dir(graph_dump_dir, graph_type, graph_level="file"):
    graph_filepath_dict = {}

    if graph_type == "all":
        graph_filepath_dict[graph_type] = os.path.join(graph_dump_dir, "export.dot")
    
    elif graph_type == "cpg":
        for root, dirs, files in os.walk(graph_dump_dir):
            for graph_dump_filename in files:
                if graph_dump_filename == "_global_.dot":
                    graph_file_filepath = os.path.join(root, graph_dump_filename)
                    file_filename = os.path.basename(root)
                    graph_filepath_dict[file_filename] = graph_file_filepath
    else:
        logger.error(f"Invalid graph type: {graph_type}, please choose from ['all', 'cpg']")

    logger.info(f"Graph file path dict: {graph_filepath_dict}")
    
    return graph_filepath_dict


def get_all_meta_filepath(root_dir = config.META_ROOT):
    meta_filepath_list = []
    meta_filename_start = config.META_FILENAME_START
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".json") or not filename.startswith(meta_filename_start):
                continue
            meta_filepath = os.path.join(root, filename)
            meta_filepath_list.append(meta_filepath)
    
    return meta_filepath_list


def get_all_code_filepath(root_dir=config.CODE_ROOT):
    code_filepath_list = []
    code_filename_start = config.CODE_FILENAME_START
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".c") or not filename.startswith(code_filename_start):
                continue
            code_filepath = os.path.join(root, filename)
            code_filepath_list.append(code_filepath)
    
    return code_filepath_list  


def build_single_slice(criterion, slice_direction, slice_type, slice_depth, node_graph_type="all", edge_graph_type="all"):
    criterion_linenum = criterion.get('criterion').get('line')
    code_filepath = criterion.get('save_file_code_old_filepath')
    filename_base = criterion.get('save_filename_base')

    graph_dir = os.path.join(os.path.dirname(code_filepath), filename_base+".graph") 
    graph_path = get_graph_save_filepath(criterion=criterion, graph_type="all_filename", level=slice_depth)

    slicer = Slicer(graph_path=graph_path)
    slice_ = slicer.build_slice(
        criterion_linenum=criterion_linenum,
        direction=slice_direction,
        g_type=slice_type,
        depth=slice_depth)

    slice_dir = graph_dir.replace(config.GRAPH_ROOT, config.SLICE_ROOT).replace(".graph", ".slice")
    # if not os.path.exists(slice_dir):
    #     os.makedirs(slice_dir)
    slice_save_path = os.path.join(slice_dir, slice_direction, slice_type, slice_depth, f"slice-{slice_direction}_{slice_type}_{slice_depth}-{filename_base}.slice_code.dot")
    if not os.path.exists(os.path.dirname(slice_save_path)):
        os.makedirs(os.path.dirname(slice_save_path))

    slicer.save_graph(
        G=slice_,
        save_path=slice_save_path)  
    
    return slice_save_path
    # if slice_scope == "function" or slice_scope == "file":
    #     get_slice_code_from_dot(file_filepath=[code_filepath], myslice_filepath=slice_save_path)
    # else:
    #     module_dirpath = criterion.get('save_module_dirpath')
    #     filepath_list = os.listdir(module_dirpath)
    #     get_slice_code_from_dot(file_filepath=filepath_list, myslice_filepath=slice_save_path)


def read_raw_function(filepath):
    with open(filepath, 'r') as f:
        return f.readlines()


def get_slice_code_from_dot_criterion(criterion, myslice_filepath, level='function'):
    code_filepath = criterion.get('save_file_code_old_filepath')
    filepath_list = [code_filepath]   
    
    if level == 'module':
        module_dirpath = criterion.get('save_module_dirpath')
        filename_list = os.listdir(module_dirpath)
        module_filepath_list = []
        for filename in filename_list:
            filepath = os.path.join(module_dirpath, filename)
            module_filepath_list.append(filepath)
        filepath_list = module_filepath_list

    # read code in each file of module
    module_code = {}
    slice_codes_dict = {}
    for file_filepath in filepath_list:
        filename = os.path.basename(file_filepath)
        module_code[filename] = read_raw_function(file_filepath)
        slice_codes_dict[filename] = {}

    # read myslice dot file
    G = nx.drawing.nx_agraph.read_dot(myslice_filepath)
    # add node code to slice_codes_dict based on file and location
    for node in G.nodes(data=True):
        node_location = node[1].get('LINE_NUMBER')
        if not node_location:
            logger.error(f"Node {node[0]} has no location")
            continue
        node_location_index = int(node_location) - 1
        node_filename = node[1].get('filename')
        if not node_filename:
            logger.error(f"Node {node[0]} has no filename")
            continue
        node_file_code = module_code[node_filename][node_location_index]
        if node_location not in slice_codes_dict[node_filename]:
            slice_codes_dict[node_filename][node_location] = node_file_code

    # sort slice_codes_dict by location
    for filename, file_slice_codes_dict in slice_codes_dict.items():
        slice_codes_dict[filename] = dict(sorted(file_slice_codes_dict.items(), key=lambda x: x[0]))

    slice_codes = []
    for filename in slice_codes_dict:
        if not slice_codes_dict[filename]:
            continue
        slice_codes.append(f"file: /* {filename} */\n")
        # slice_codes.extend(list(slice_codes_dict[filename].values()))    
        for location, code in slice_codes_dict[filename].items():
            slice_codes.append(f"{location}: {code}")
    
    all_nodes_list = {node[0]:node[1] for node in G.nodes(data=True)}
    all_edges_list = [{f"{edge[0]}->{edge[1]}":edge[-1]} for edge in G.edges(data=True)]

    slice_info_dict = {
        'code': slice_codes_dict,
        'nodes': all_nodes_list,
        'edges': all_edges_list
    }

    codes_dict_save_filepath = myslice_filepath.replace('.dot', '.slice_code.json')
    with open(codes_dict_save_filepath, 'w') as f:
        f.write(json.dumps(slice_info_dict, indent=4))
    slice_codes_save_filepath = myslice_filepath.replace('.dot', '.slice_code')
    with open(slice_codes_save_filepath, 'w') as f:
        f.writelines(slice_codes)
    
    print(codes_dict_save_filepath)
    print(slice_codes_save_filepath)
 

def get_slice_code_from_dot(filepath_list, myslice_filepath):
    module_code = {}
    for file_filepath in filepath_list:
        filename = os.path.basename(file_filepath)
        module_code[filename] = read_raw_function(file_filepath)
    slice_codes_dict = {}
    slice_codes = []
    G = nx.drawing.nx_agraph.read_dot(myslice_filepath)
    for node in G.nodes(data=True):
        node_location = node[1].get('location')
        node_location_index = int(node_location) - 1
        node_file_code = module_code[filename][node_location_index]
        if node_location not in slice_codes_dict:
            slice_codes_dict[node_location] = node_file_code

    all_nodes_list = {node[0]:node[1] for node in G.nodes(data=True)}
    all_edges_list = [edge[-1] for edge in G.edges(data=True)]
    slice_codes_dict = dict(sorted(slice_codes_dict.items(), key=lambda x: x[0]))
    slice_codes = list(slice_codes_dict.values())

    slice_codes_dict = {
        'code': slice_codes_dict,
        'nodes': all_nodes_list,
        'edges': all_edges_list
    }

    codes_dict_save_filepath = myslice_filepath.replace('.dot', '.slice_code.json')
    with open(codes_dict_save_filepath, 'w') as f:
        f.write(json.dumps(slice_codes_dict, indent=4))
    slice_codes_save_filepath = myslice_filepath.replace('.dot', '.slice_code.c')
    with open(slice_codes_save_filepath, 'w') as f:
        f.writelines(slice_codes)
    
    print(codes_dict_save_filepath)
    print(slice_codes_save_filepath)


def add_filename_to_all_graph(criterion, level):
    graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
    graph_dump_dir_all = get_graph_dump_dir(graph_dir, "all")
    graph_dump_dir_cpg = get_graph_dump_dir(graph_dir, "cpg")

    graph_filepath_dict_all = get_graph_filepath_from_dump_dir(graph_dump_dir_all, "all")
    graph_filepath_dict_cpg = get_graph_filepath_from_dump_dir(graph_dump_dir_cpg, "cpg")

    graph_builder = GraphBuilder()
    # read graph from graph_filepath
    graph_filepath_all = graph_filepath_dict_all['all']
    G_all = graph_builder.read_graph(graph_filepath_all)
    # get filename from cpg_graph_dir
    for file_filename, graph_filepath_cpg in graph_filepath_dict_cpg.items():
        if not os.path.exists(graph_filepath_cpg):
            logger.error(f"File graph not found: {graph_filepath_cpg}")
            continue
        # read cpg_graph from file_graph_filepath
        G_cpg = graph_builder.read_graph(graph_filepath_cpg)
        # get nodes from cpg_graph
        cpg_nodes = G_cpg.nodes(data=True)
        # match nodes from cpg_graph to all_graph, and add filename to all_graph
        for node in cpg_nodes:
            node_id = node[0]
            if node_id in G_all.nodes():
                G_all.nodes[node_id]['filename'] = file_filename

    # save all_graph to graph_filepath
    graph_save_filepath = get_graph_save_filepath(criterion=criterion, graph_type="all_filename", level=level)
    graph_builder.save_graph(graph_save_filepath, G_all)


def get_graph_save_filepath(criterion, graph_type, level):
    graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
    filename_base = criterion.get('save_filename_base')
    graph_save_path = os.path.join(graph_dir, "-".join([config.GRAPH_START, filename_base, graph_type+config.GRAPH_FILE_END]))
    return graph_save_path



def slice_from_patch():
    url = config.LINUX
    hash_id = "0844370f8945086eb9335739d10205dcea8d707b"
    extractor = CriterionExtractor(url=url, hash_id=hash_id)
    criterions = extractor.get_criterion_from_patch()
    extractor.save_criterion(criterions=criterions)
    # # # exit()
    graph_type = "all"
    graph_level = "module"
    hash_id_short = hash_id[:8]
    code_dir = os.path.join(config.CODE_ROOT, hash_id_short)
    graph_dir = build_level_graph(graph_type=graph_type, code_dir=code_dir, confirm=config.BIN_CONFIRM, level=graph_level, overwrite=config.BIN_OVERWRITE)
    graph_dir = build_level_graph(graph_type="cpg", code_dir=code_dir, confirm=config.BIN_CONFIRM, level=graph_level, overwrite=config.BIN_OVERWRITE)
    
    for criterion in criterions:
        node_graph_type = "all"
        edge_graph_type = "all"
        slice_direction = "backward"
        slice_type = "cfg"
        slice_depth = graph_level
        add_filename_to_all_graph(criterion, level=slice_depth) 
        slice_save_path = build_single_slice(
            criterion=criterion,
            node_graph_type=node_graph_type,
            edge_graph_type=edge_graph_type,
            slice_direction=slice_direction,
            slice_type=slice_type,
            slice_depth=slice_depth)
        
        get_slice_code_from_dot_criterion(criterion=criterion, myslice_filepath=slice_save_path, level=slice_depth)


    
if __name__ == '__main__':
    import time
    start_time = time.time()

    slice_from_patch()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Program executed in {elapsed_time:.2f} seconds")