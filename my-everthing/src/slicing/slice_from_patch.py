import os
from icecream import ic
import re
import json
import networkx as nx

from patch_analyzer import PatchAnalyzer
from graph_builder import GraphBuilder
from criterion_extractor import CriterionExtractor
from slicer import Slicer
import config

import logging
logger = logging.getLogger(__name__)

import log_config
log_config.setup_logging()


def build_graph_from_file_code(graph_type="all", code_dir=config.CODE_ROOT):
    """Builds graphs from the code files in the code directory.
        1) get the code file path (CODE_ROOT/commit_id/{filename}.c)
        2) parse the code file, and save the binary file (.bin) to the graph directory (.graph)
        3) dump the graph (.dot) from the binary file to the graph directory (.graph)

    Parameters:
        graph_type (str): The type of graph to build. Default is 'all'.   
    """
    graph_builder = GraphBuilder()
    code_filepath_list = get_code_filepath(code_dir=code_dir)

    for code_filepath in code_filepath_list:
        graph_dir = code_filepath.replace(config.CODE_ROOT, config.GRAPH_ROOT).replace(".c", ".graph")
        filename = os.path.basename(code_filepath)
    
        if not os.path.exists(graph_dir):
            os.makedirs(graph_dir) 
        bin_file = os.path.join(graph_dir, f"{filename}.bin")
        if os.path.exists(bin_file):
            reget_bin = input(f"bin file exists, regenerate bin file for {filename}? (y/n)")
            if reget_bin == "y":
                os.remove(bin_file)
                graph_builder.joern_parse(code_filepath, bin_file)
        else:
            graph_builder.joern_parse(code_filepath, bin_file)

        # graph_type = "all"
        graph_dump_dir = os.path.join(graph_dir, "graph_"+graph_type)
        graph_builder.joern_dump_graph(graph_dir=graph_dump_dir, bin_file=bin_file, graph_type=graph_type)

        graph_path = get_graph_filepath_from_dump_dir(graph_dump_dir, graph_type)
        save_path = os.path.join(graph_dir, f"graph_{graph_type}-{filename}.dot")
        if not graph_path:
            try:
                G_combine = graph_builder.combine_graph_in_dir(graph_dump_dir)
                graph_builder.save_graph(save_path, G_combine)
            except Exception as e:
                ic(e)
                logger.error(f"[build_graph_from_file_code] Error: {e}")
        if graph_path and os.path.exists(graph_path):
            os.system(f"cp {graph_path} {save_path}")

        ic(save_path)
        logger.info(f"[build_graph_from_file_code] Graph saved to {save_path}")


def build_graph_from_file_code_level(graph_type="all", code_dir=config.CODE_ROOT, level='function'):
    """Builds graphs from the code files in the code directory.
        1) get the code file path (CODE_ROOT/commit_id/{filename}.c)
        2) parse the code file, and save the binary file (.bin) to the graph directory (.graph)
        3) dump the graph (.dot) from the binary file to the graph directory (.graph)

    Parameters:
        graph_type (str): The type of graph to build. Default is 'all'.   
    """
    graph_builder = GraphBuilder()
    code_filepath_list = get_code_filepath(code_dir=code_dir)

    for code_filepath in code_filepath_list:
        graph_dir = code_filepath.replace(config.CODE_ROOT, config.GRAPH_ROOT).replace(".c", ".graph")
        filename = os.path.basename(code_filepath)
    
        if not os.path.exists(graph_dir):
            os.makedirs(graph_dir) 
        bin_file = os.path.join(graph_dir, f"{filename}.bin")
        if os.path.exists(bin_file):
            reget_bin = input(f"bin file exists, regenerate bin file for {filename}? (y/n)")
            if reget_bin == "y":
                os.remove(bin_file)
                graph_builder.joern_parse(code_filepath, bin_file)
        else:
            graph_builder.joern_parse(code_filepath, bin_file)

        # graph_type = "all"
        graph_dump_dir = os.path.join(graph_dir, "graph_"+graph_type)
        graph_builder.joern_dump_graph(graph_dir=graph_dump_dir, bin_file=bin_file, graph_type=graph_type)

        graph_path = get_graph_filepath_from_dump_dir(graph_dump_dir, graph_type)
        save_path = os.path.join(graph_dir, f"graph_{graph_type}-{filename}.dot")
        if not graph_path:
            try:
                G_combine = graph_builder.combine_graph_in_dir(graph_dump_dir)
                graph_builder.save_graph(save_path, G_combine)
            except Exception as e:
                ic(e)
                logger.error(f"[build_graph_from_file_code] Error: {e}")
        if graph_path and os.path.exists(graph_path):
            os.system(f"cp {graph_path} {save_path}")

        ic(save_path)
        logger.info(f"[build_graph_from_file_code] Graph saved to {save_path}")


def get_graph_filepath_from_dump_dir(graph_dump_dir, graph_type):
    graph_filepath = ""
    if graph_type == "all":
        graph_filepath = os.path.join(graph_dump_dir, "export.dot")
    elif graph_type == "cpg":
        graph_filepath = os.path.join(graph_dump_dir, "_global_.dot")
    else:
        # raise ValueError(f"Invalid graph type: {graph_type}")
        ic(f"Invalid graph type: {graph_type}")
        logger.error(f"[get_graph_filepath_from_dump_dir] Invalid graph type: {graph_type}")

    ic(graph_filepath)
    logger.info(f"[get_graph_filepath_from_dump_dir] Graph file path: {graph_filepath}")
    return graph_filepath


def _get_code_filepath(code_dir=config.CODE_ROOT):
    code_filepath_list = []
    # code_dir = config.CODE_ROOT
    code_commit_ids = os.listdir(code_dir)
    for commit_id in code_commit_ids:
        commit_id_dir = os.path.join(code_dir, commit_id)
        code_filenames = os.listdir(commit_id_dir)
        for filename in code_filenames:
            if not filename.endswith(".c"):
                continue            

            code_filepath = os.path.join(code_dir, commit_id, filename)
            code_filepath_list.append(code_filepath)
    
    return code_filepath_list  


def get_code_filepath(code_dir=config.CODE_ROOT):
    code_filepath_list = []
    code_filename_start = config.CODE_FILENAME_START
    for root, dirs, files in os.walk(code_dir):
        for file in files:
            if not file.endswith(".c") or not file.startswith(code_filename_start):
                continue
            code_filepath = os.path.join(root, file)
            code_filepath_list.append(code_filepath)
    
    return code_filepath_list  


def build_single_slice(code_filepath, slice_direction, slice_type, slice_scope, node_graph_type="all", edge_graph_type="all"):
    filename = os.path.basename(code_filepath)
    filename_pattern = r'file_code_old-(\w+)-(\w+)-(\d+).c'
    regex_result = re.search(filename_pattern, filename)
    if not regex_result:
        ic('no commit id or line number', code_filepath)
        logger.error(f"[build_single_slice] No commit id or line number in {code_filepath}")
        return

    commit_id = regex_result.group(1)
    criterion_linenum = regex_result.group(3)
    graph_dir = code_filepath.replace(config.CODE_ROOT, config.GRAPH_ROOT).replace(".c", ".graph")
    node_graph_filename = f"graph_{node_graph_type}-{filename}.dot"
    node_graph_path = os.path.join(graph_dir, node_graph_filename)
    edge_graph_filename = f"graph_{edge_graph_type}-{filename}.dot"
    edge_graph_path = os.path.join(graph_dir, edge_graph_filename)

    slicer = Slicer(node_graph_path=edge_graph_path, edge_graph_path=edge_graph_path)
    slice_ = slicer.build_slice(
        criterion_linenum=criterion_linenum,
        direction=slice_direction,
        g_type=slice_type,
        depth=slice_scope)

    slice_dir = graph_dir.replace(config.GRAPH_ROOT, config.SLICE_ROOT).replace(".graph", ".slice")
    if not os.path.exists(slice_dir):
        os.makedirs(slice_dir)
    slice_save_path = os.path.join(slice_dir, f"slice-{slice_direction}_{slice_type}_{slice_scope}-{filename}.slice_code.dot")    
    slicer.save_graph(
        G=slice_,
        save_path=slice_save_path)  
    
    get_slice_code_from_dot(file_filepath=code_filepath, myslice_filepath=slice_save_path)


def read_raw_function(filepath):
    with open(filepath, 'r') as f:
        return f.readlines()


def get_slice_code_from_dot(file_filepath, myslice_filepath):
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


def get_single_code_filepath_from_criterion(criterion:dict):
    commit_id = criterion.get('commit_id')
    commit_id_short = commit_id[:8]
    criterion_line = criterion.get('criterion').get('line')
    # filename = f"file_code_old-{commit_id_short}_{criterion_line}.c"
    func_name = criterion.get('func_name')
    funcname_line = "-".join([func_name, str(criterion_line)])
    filename = "-".join([config.CODE_FILENAME_START, commit_id_short, funcname_line]) + '.c'
    code_filepath = os.path.join(config.CODE_ROOT, commit_id_short, funcname_line, filename)
    return code_filepath


def slice_from_patch():
    url = config.LINUX
    hash_id = "0844370f8945086eb9335739d10205dcea8d707b"
    extractor = CriterionExtractor(url=url, hash_id=hash_id)
    criterions = extractor.get_criterion_from_patch()
    # extractor.save_criterion(criterions=criterions)
    # # exit()
    # graph_type = "all"
    # hash_id_shot = hash_id[:8]
    # code_dir = os.path.join(config.CODE_ROOT, hash_id_shot)
    # build_graph_from_file_code(graph_type=graph_type, code_dir=code_dir)

    # ic(len(criterions))
    # criterion = criterions[0]
    for criterion in criterions:
        code_filepath = get_single_code_filepath_from_criterion(criterion)
        node_graph_type = "all"
        edge_graph_type = "all"
        slice_direction = "backward"
        slice_type = "pdg"
        slice_scope = "file"
        build_single_slice(
            code_filepath=code_filepath,
            node_graph_type=node_graph_type,
            edge_graph_type=edge_graph_type,
            slice_direction=slice_direction,
            slice_type=slice_type,
            slice_scope=slice_scope)

if __name__ == '__main__':
    slice_from_patch()
