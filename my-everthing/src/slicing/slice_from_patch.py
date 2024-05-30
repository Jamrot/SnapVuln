import os
from icecream import ic
import re
import json
import networkx as nx
from tqdm import tqdm

from patch_analyzer import PatchAnalyzer
from graph_builder import GraphBuilder
from criterion_extractor import CriterionExtractor
from slicer import Slicer
import config

import logging
logger = logging.getLogger(__name__)

import log_config
log_config.setup_logging()


def build_level_graph(code_dir, graph_type="all", level='function', confirm=True, overwrite='n'):
    graph_builder = GraphBuilder()
    meta_filepath_list = get_meta_filepath(meta_dir=code_dir)
    for meta_filepath in meta_filepath_list:
        with open(meta_filepath, 'r') as f:
            criterion = json.load(f)
        if not len(criterion)==1:
            logger.error(f"[build_graph_from_dir] Invalid criterion from meta file: {meta_filepath}")
            continue
        criterion = criterion[0]

        # get module and code filepath
        module_path = criterion.get('save_module_dirpath')
        code_filepath = criterion.get('save_file_code_old_filepath')
        if not os.path.exists(module_path):
            logger.error(f"[build_graph_from_dir] Module file not found: {module_path}")
            continue
        if not os.path.exists(code_filepath):
            logger.error(f"[build_graph_from_dir] Code file not found: {code_filepath}")
            continue
        
        # set graph dir and filename
        # filename = os.path.basename(meta_filepath).replace(config.META_FILENAME_START, "").replace(".json", "")
        filename_base = criterion.get('save_filename_base')
        graph_dir = os.path.join(os.path.dirname(meta_filepath), filename_base+".graph")  

        # choose parse path based on level
        if level=="function" or level=="file":
            parse_path = code_filepath
        elif level=="module":
            parse_path = module_path
        else:
            logger.error(f"[build_graph_from_dir] Invalid parse level: {level}")
            continue
        
        # parse graph (generate bin file)
        if not os.path.exists(graph_dir):
            os.makedirs(graph_dir) 
        bin_filepath = os.path.join(graph_dir, f"{level}-{filename_base}.bin")
        if os.path.exists(bin_filepath):
            confirm_input = input(f"bin file {bin_filepath} already exists, overwrite? (y/n)") if confirm else overwrite
            if confirm_input == "y":
                os.remove(bin_filepath)
                graph_builder.joern_parse(parse_path, bin_filepath)
        else:
            graph_builder.joern_parse(parse_path, bin_filepath)
        
        # dump graph (generate dot file)
        graph_dump_dir = os.path.join(graph_dir, "graph_"+graph_type)
        graph_builder.joern_dump_graph(graph_dir=graph_dump_dir, bin_file=bin_filepath, graph_type=graph_type)

        graph_path_dict = get_graph_filepath_from_dump_dir(graph_dump_dir=graph_dump_dir, criterion=criterion, graph_type=graph_type)
        for file_filename, graph_filepath in graph_path_dict.items():
               
            graph_save_path = os.path.join(graph_dir, f"graph_{graph_type}-{filename_base}-{file_filename}.dot")
            
            logger.info(f"[build_graph_from_file_code] Graph path: {graph_filepath}")
            if graph_filepath and os.path.exists(graph_filepath):
                os.system(f"cp {graph_filepath} {graph_save_path}")
            else:
                try:
                    G_combine = graph_builder.combine_graph_in_dir(graph_dump_dir)
                    graph_builder.save_graph(graph_save_path, G_combine)
                except Exception as e:
                    logger.error(f"[build_graph_from_file_code] Error: {e}")

            logger.info(f"[build_graph_from_file_code] Graph saved to {graph_save_path}")
    
    return graph_dir


def get_graph_filepath_from_dump_dir(graph_dump_dir, criterion, graph_type):
    """"""
    graph_filepath = {}
    if graph_type == "all":
        graph_filepath['all'] = os.path.join(graph_dump_dir, "export.dot")
    elif graph_type == "cpg":
        # get every file's graph file path
        module_dirpath = criterion.get('save_module_dirpath')
        file_filename_list = os.listdir(module_dirpath)
        for file_filename in file_filename_list:
            file_graph_filepath = os.path.join(graph_dump_dir, file_filename, '_global_.dot')
            if not os.path.exists(file_graph_filepath):
                logger.error(f"[get_graph_filepath_from_dump_dir] File graph not found: {file_graph_filepath}")
                continue
            graph_filepath[file_filename] = file_graph_filepath
    else:
        # raise ValueError(f"Invalid graph type: {graph_type}")
        ic(f"Invalid graph type: {graph_type}")
        logger.error(f"[get_graph_filepath_from_dump_dir] Invalid graph type: {graph_type}")

    ic(graph_filepath)
    logger.info(f"[get_graph_filepath_from_dump_dir] Graph file path: {graph_filepath}")
    return graph_filepath


def get_meta_filepath(meta_dir = config.CODE_ROOT):
    meta_filepath_list = []
    meta_filename_start = config.META_FILENAME_START
    for root, dirs, files in os.walk(meta_dir):
        for filename in files:
            if not filename.endswith(".json") or not filename.startswith(meta_filename_start):
                continue
            meta_filepath = os.path.join(root, filename)
            meta_filepath_list.append(meta_filepath)
    
    return meta_filepath_list


def get_code_filepath(code_dir=config.CODE_ROOT):
    code_filepath_list = []
    code_filename_start = config.CODE_FILENAME_START
    for root, dirs, files in os.walk(code_dir):
        for filename in files:
            if not filename.endswith(".c") or not filename.startswith(code_filename_start):
                continue
            code_filepath = os.path.join(root, filename)
            code_filepath_list.append(code_filepath)
    
    return code_filepath_list  


def build_single_slice(criterion, slice_direction, slice_type, slice_scope, node_graph_type="all", edge_graph_type="all"):
    criterion_linenum = criterion.get('criterion').get('line')
    code_filepath = criterion.get('save_file_code_old_filepath')
    filename_base = criterion.get('save_filename_base')

    graph_dir = os.path.join(os.path.dirname(code_filepath), filename_base+".graph")  
    node_graph_filename = f"graph_{node_graph_type}-{filename_base}-all.dot"
    node_graph_path = os.path.join(graph_dir, node_graph_filename)
    edge_graph_filename = f"graph_{edge_graph_type}-{filename_base}-all.dot"
    edge_graph_path = os.path.join(graph_dir, edge_graph_filename)

    slicer = Slicer(node_graph_path=node_graph_path, edge_graph_path=edge_graph_path)
    slice_ = slicer.build_slice(
        criterion_linenum=criterion_linenum,
        direction=slice_direction,
        g_type=slice_type,
        depth=slice_scope)

    slice_dir = graph_dir.replace(config.GRAPH_ROOT, config.SLICE_ROOT).replace(".graph", ".slice")
    # if not os.path.exists(slice_dir):
    #     os.makedirs(slice_dir)
    slice_save_path = os.path.join(slice_dir, slice_direction, slice_type, slice_scope, f"slice-{slice_direction}_{slice_type}_{slice_scope}-{filename_base}.slice_code.dot")
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

    module_code = {}
    slice_codes_dict = {}
    for file_filepath in filepath_list:
        filename = os.path.basename(file_filepath)
        module_code[filename] = read_raw_function(file_filepath)
        slice_codes_dict[filename] = {}

    slice_codes = []
    G = nx.drawing.nx_agraph.read_dot(myslice_filepath)
    for node in G.nodes(data=True):
        node_location = node[1].get('location')
        node_location_index = int(node_location) - 1
        node_filename = node[1].get('filename')
        node_file_code = module_code[node_filename][node_location_index]
        if node_location not in slice_codes_dict[node_filename]:
            slice_codes_dict[node_filename][node_location] = node_file_code

    all_nodes_list = {node[0]:node[1] for node in G.nodes(data=True)}
    all_edges_list = [edge[-1] for edge in G.edges(data=True)]
    slice_codes = []
    for filename, file_slice_codes_dict in slice_codes_dict.items():
        slice_codes_dict[filename] = dict(sorted(file_slice_codes_dict.items(), key=lambda x: x[0]))

    for filename in slice_codes_dict:
        if not slice_codes_dict[filename]:
            continue
        slice_codes.append(f"/* {filename} */\n")
        slice_codes.extend(list(slice_codes_dict[filename].values()))    

    slice_codes_dict = {
        'code': slice_codes_dict,
        'nodes': all_nodes_list,
        'edges': all_edges_list
    }

    codes_dict_save_filepath = myslice_filepath.replace('.dot', '.slice_code.json')
    with open(codes_dict_save_filepath, 'w') as f:
        f.write(json.dumps(slice_codes_dict, indent=4))
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


def add_filename_to_all_graph(all_graph_filepath, cpg_graph_dir):
    graph_builder = GraphBuilder()
    # read graph from graph_filepath
    G_all = graph_builder.read_graph(all_graph_filepath)
    # get filename from cpg_graph_dir
    file_filename_list = os.listdir(cpg_graph_dir)
    for file_filename in tqdm(file_filename_list):
        file_graph_filepath = os.path.join(cpg_graph_dir, file_filename, '_global_.dot')
        if not os.path.exists(file_graph_filepath):
            logger.error(f"[get_graph_filepath_from_dump_dir] File graph not found: {file_graph_filepath}")
            continue
        # read cpg_graph from file_graph_filepath
        G_cpg = graph_builder.read_graph(file_graph_filepath)
        # get nodes from cpg_graph
        cpg_nodes = G_cpg.nodes(data=True)
        # match nodes from cpg_graph to all_graph, and add filename to all_graph
        for node in cpg_nodes:
            node_id = node[0]
            if node_id in G_all.nodes():
                G_all.nodes[node_id]['filename'] = file_filename                
    # save all_graph to graph_filepath
    graph_builder.save_graph(all_graph_filepath, G_all)

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
    graph_dir = build_level_graph(graph_type=graph_type, code_dir=code_dir, confirm=config.BIN_CONFIRM, level=graph_level, overwrite='n')
    graph_dir = build_level_graph(graph_type="cpg", code_dir=code_dir, confirm=config.BIN_CONFIRM, level=graph_level, overwrite='n')
    cpg_graph_dir = os.path.join(graph_dir, "graph_cpg")

    ic(len(criterions))
    for criterion in criterions:
        node_graph_type = graph_type
        edge_graph_type = graph_type
        slice_direction = "backward"
        slice_type = "pdg"
        slice_scope = graph_level
        slice_save_path = build_single_slice(
            criterion=criterion,
            node_graph_type=node_graph_type,
            edge_graph_type=edge_graph_type,
            slice_direction=slice_direction,
            slice_type=slice_type,
            slice_scope=slice_scope)
        
        add_filename_to_all_graph(all_graph_filepath=slice_save_path, cpg_graph_dir=cpg_graph_dir)
        get_slice_code_from_dot_criterion(criterion=criterion, myslice_filepath=slice_save_path, level=slice_scope)

def read_criterion_from_meta(meta_filepath):
    with open(meta_filepath, 'r') as f:
        return json.load(f)

def test_get_code():
    meta_filepath = "my-everthing/data/test/0844370f/tls_strp_msg_ready-218/meta-0844370f-tls_strp_msg_ready-218.json"
    criterions=read_criterion_from_meta(meta_filepath=meta_filepath)
    criterion = criterions[0]
    myslice_filepath="my-everthing/data/test/0844370f/tls_strp_msg_ready-218/0844370f-tls_strp_msg_ready-218.slice/backward/pdg/module/slice-backward_pdg_module-0844370f-tls_strp_msg_ready-218.slice_code.dot"
    level="module"
    get_slice_code_from_dot_criterion(criterion, myslice_filepath, level)

def _test_add_filename_to_all_graph():
    # url = config.LINUX
    # hash_id = "0844370f8945086eb9335739d10205dcea8d707b"
    # extractor = CriterionExtractor(url=url, hash_id=hash_id)
    # criterions = extractor.get_criterion_from_patch()
    # extractor.save_criterion(criterions=criterions)
    
    # graph_type = "all"
    # graph_level = "module"
    # hash_id_short = hash_id[:8]
    # code_dir = os.path.join(config.CODE_ROOT, hash_id_short)
    # build_level_graph(graph_type=graph_type, code_dir=code_dir, confirm=config.BIN_CONFIRM, level=graph_level)

    # graph_type = "cpg"
    # graph_level = "module"
    # hash_id_short = hash_id[:8]
    # code_dir = os.path.join(config.CODE_ROOT, hash_id_short)
    # build_level_graph(graph_type=graph_type, code_dir=code_dir, confirm=True, level=graph_level)

    all_graph_filepath = "my-everthing/data/test/0844370f/tls_strp_msg_ready-218/0844370f-tls_strp_msg_ready-218.slice/backward/pdg/module/slice-backward_pdg_module-0844370f-tls_strp_msg_ready-218.slice_code.dot"
    cpg_graph_dir = "my-everthing/data/test/0844370f/tls_strp_msg_ready-218/0844370f-tls_strp_msg_ready-218.graph/graph_cpg"
    add_filename_to_all_graph(all_graph_filepath=all_graph_filepath, cpg_graph_dir=cpg_graph_dir)


    
if __name__ == '__main__':
    slice_from_patch()
    # test_get_code()
    # _test_add_filename_to_all_graph()
