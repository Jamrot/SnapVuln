import os
import re
import json
import networkx as nx
from tqdm import tqdm

from analysis.patch_analyzer import PatchAnalyzer
from analysis.graph_builder import GraphBuilder
from analysis.criterion_extractor import CriterionExtractor
from slices.slicer_new import Slicer
import config.config as config
import utils.get_path as get_path
import api_requests.response_parser as response_parser
import slices.get_slice_results as get_slice_results

import logging
logger = logging.getLogger(__name__)

# from slices.slice_from_patch import *

def build_level_graph(root_dir, graph_type="all", level='function'):
    graph_builder = GraphBuilder()
    meta_filepath_list = get_all_meta_filepath(root_dir=root_dir)
    
    for meta_filepath in meta_filepath_list:
        criterion = read_criterion_from_meta(meta_filepath=meta_filepath)
        graph_dir = get_path.get_graph_dir_from_criterion(criterion=criterion, level=level)
        joern_parse_path = get_path.get_joern_parse_path_from_criterion(criterion=criterion, level=level)
        # check path validation
        if not graph_dir or not joern_parse_path:
            logger.error(f"Invalid graph_dir or parse_path: {graph_dir}, {joern_parse_path}")
            continue
        if not os.path.exists(graph_dir):
            os.makedirs(graph_dir)

        bin_filepath = get_path.get_bin_filepath_from_criterion(criterion=criterion, level=level)
        if config.BIN_OVERWRITE or not os.path.exists(bin_filepath):
            graph_builder.joern_parse(source_path=joern_parse_path, bin_file=bin_filepath)
        
        graph_dump_dir = get_path.get_graph_dump_dir(graph_dump_dir=graph_dir, bin_filepath=bin_filepath, graph_dump_type=graph_type)
        if config.GRAPH_OVERWRITE or not os.path.exists(graph_dump_dir):
            graph_builder.joern_dump_graph(graph_dir=graph_dump_dir, bin_file=bin_filepath, graph_type=graph_type)

        # save_graph_file(graph_dump_dir=graph_dump_dir, criterion=criterion, graph_type=graph_type)
    
    return graph_dir

"""
build graph from meta file
1. function level / file level
    1) first file dot -> grpah dir
    2) check if file dot exists
"""

def read_criterion_from_meta(meta_filepath):
    with open(meta_filepath, 'r') as f:
        criterion = json.load(f)
    if not len(criterion)==1:
        logger.error(f"Invalid criterion from meta file: {meta_filepath}")
        return None
    criterion = criterion[0]
    return criterion


def save_graph_file(graph_dump_dir, criterion, graph_type, level):
    graph_dir = get_path.get_graph_dir_from_criterion(criterion=criterion, level=level)
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
                    break
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


def get_all_code_filepath(root_dir=config.CODE_DIRNAME):
    code_filepath_list = []
    code_filename_start = config.CODE_FILENAME_START
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if not filename.endswith(".c") or not filename.startswith(code_filename_start):
                continue
            code_filepath = os.path.join(root, filename)
            code_filepath_list.append(code_filepath)
    
    return code_filepath_list  


def build_single_slice(criterion, slice_direction, slice_graph, slice_depth, graph_type="all", G_grpah=None):
    criterion_linenum = criterion.get('criterion').get('line')
    code_filepath = criterion.get('save_file_code_old_filepath')
    filename_base = criterion.get('save_filename_base')
    
    if not G_grpah:
        graph_path = get_path.get_graph_savepath_from_criterion(criterion=criterion, graph_type=graph_type, level=slice_depth)
        G_grpah = nx.drawing.nx_agraph.read_dot(graph_path)

    slicer = Slicer(G_graph=G_grpah)
    G_slice = slicer.build_slice(
        criterion_linenum=criterion_linenum,
        direction=slice_direction,
        g_type=slice_graph,
        depth=slice_depth)

    slice_save_path = get_path.get_slice_savepath_from_criterion(criterion=criterion, direction=slice_direction, graph_type=slice_graph, depth=slice_depth)
    if not os.path.exists(os.path.dirname(slice_save_path)):
        os.makedirs(os.path.dirname(slice_save_path))

    slicer.save_graph(
        G=G_slice,
        save_path=slice_save_path)  
    
    return slice_save_path, G_slice


def add_filename_to_all_graph(criterion, level):
    graph_save_filepath = get_path.get_graph_savepath_from_criterion(criterion=criterion, graph_type="all_filename", level=level)
    if os.path.exists(graph_save_filepath) and not config.GRAPH_ALL_OVERWRITE:
        logging.warning(f"{graph_save_filepath} already exists and not overwrite, return G_all.")
        G_all = nx.drawing.nx_agraph.read_dot(graph_save_filepath)
        return G_all

    graph_dump_dir = get_path.get_graph_dir_from_criterion(criterion=criterion, level=level)
    bin_filepath = get_path.get_bin_filepath_from_criterion(criterion=criterion, level=level)
    graph_dump_dir_all = get_path.get_graph_dump_dir(graph_dump_dir=graph_dump_dir, bin_filepath=bin_filepath, graph_dump_type="all")
    graph_dump_dir_cpg = get_path.get_graph_dump_dir(graph_dump_dir=graph_dump_dir, bin_filepath=bin_filepath, graph_dump_type="cpg")

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
    graph_builder.save_graph(graph_save_filepath, G_all)

    return G_all


def match_criterion_from_response(parsed_response, criterions):
    # criterion: {'line': int, 'code': str}, commit_id: str, version: {'old': str, 'new': str}, file_path: {'old': str, 'new': str}, func_name: str, func_line: {'start': int, 'end': int}, func_code: {'old': str, 'new': str}, file_code: {'old': str, 'new': str}, modification: str

    matched_criterions = []
    slicing_direction = ""
    slicing_graph = ""

    criterions_dict = {}
    for criterion in criterions:
        file_path = criterion['file_path']
        func_name = criterion['func_name']
        stmt_info = criterion['criterion']
        modification = criterion['modification']
        criterion_info, _ = response_parser.get_line_info(file_path, func_name, stmt_info, modification)
        criterions_dict[criterion_info] = criterion
    
    parsed_stmts = parsed_response['slicing_statements']
    for stmt_id in parsed_stmts:
        stmt = parsed_stmts[stmt_id]
        stmt_info = stmt['statement_info']
        if stmt_info in criterions_dict:
            matched_criterion = criterions_dict[stmt_info]
            matched_criterion['direction'] = get_response_direction(stmt['slicing_direction'])
            matched_criterion['graph'] = get_response_graph_type(stmt['code_representation_graph'])
            matched_criterions.append(matched_criterion)
            logging.info(f"Matched criterion: {stmt_info}")
        else:
            logging.error(f"No matched criterion: {stmt_info}")

    return matched_criterions


def get_response_graph_type(response_graph_type):
    if response_graph_type == "Control Flow Graph":
        graph_type = "cfg"
    elif response_graph_type == "Program Dependence Graph":
        graph_type = "pdg"
    elif response_graph_type == "Data Dependency Graph":
        graph_type = "ddg"
    elif response_graph_type == "Control Dependency Graph":
        graph_type = "cdg"
    elif response_graph_type == "Abstract Syntax Tree":
        graph_type = "ast"
    elif response_graph_type == "Code Property Graph":
        graph_type = "cpg"
    elif response_graph_type == "Call Graph":
        graph_type = "cg"
    else:
        logging.error(f"Invalid graph type: {response_graph_type}")
        graph_type = "all"
    
    return graph_type


def get_response_direction(response_direction):
    if response_direction not in ['forward', 'backward', 'bidirectional']:
        logging.error(f"Invalid slicing direction: {response_direction}")
        response_direction = "bidirectional"
    
    return response_direction


def slice_from_response():
    url = config.LINUX
    commit_id = config.COMMIT_ID
    extractor = CriterionExtractor(url=url, commit_id=commit_id)
    criterions = extractor.get_criterion_from_patch()
    
    # get matched criterions from response
    parsed_filepath = config.PARSED_FILEPATH
    parsed_response = response_parser.read_parsed_response(response_filepath=parsed_filepath)
    matched_criterions = match_criterion_from_response(parsed_response, criterions)    
    extractor.save_criterion(criterions=matched_criterions)

    # set graph build root path
    criterion_root_dir = get_path.get_save_root(commit_id=commit_id)

    # set graph type and level
    graph_type = "all"
    graph_level = "file" # function, file, module    

    graph_dir = build_level_graph(graph_type=graph_type, root_dir=criterion_root_dir, level=graph_level)
    graph_dir = build_level_graph(graph_type="cpg", root_dir=criterion_root_dir, level=graph_level)
    
    dict_G_all = {} # dict for all nodes and edges graph
    for criterion in matched_criterions:
        graph_save_path = get_path.get_graph_savepath_from_criterion(criterion=criterion, graph_type="all_filename", level=graph_level)
        if graph_save_path not in dict_G_all:
            G_all = add_filename_to_all_graph(criterion=criterion, level=graph_level) 
            dict_G_all[graph_save_path] = G_all
    
    G_all = None
    collate_info_dict = {'code':{}, 'nodes':{}, 'edges':{}}
    collate_codes = []
    for criterion in matched_criterions:
        # graph_type = "all"
        graph_save_path = get_path.get_graph_savepath_from_criterion(criterion=criterion, graph_type="all_filename", level=graph_level)
        slice_direction = criterion['direction']
        slice_graph = criterion['graph']
        slice_depth = graph_level
        G_all = dict_G_all[graph_save_path]
        slice_save_path, G_slice = build_single_slice(
            criterion=criterion,
            slice_direction=slice_direction,
            slice_graph=slice_graph,
            slice_depth=slice_depth,
            graph_type=graph_type,
            G_grpah=G_all)
        
        slice_save_path = get_path.get_slice_savepath_from_criterion(criterion=criterion, direction=slice_direction, graph_type=slice_graph, depth=slice_depth)

        slice_info_dict = get_slice_results.get_slice_info_from_dot_criterion(criterion=criterion, myslice_filepath=slice_save_path, level=slice_depth, G_slice=None)
        get_slice_results.get_slice_codes_from_info(slice_info_dict=slice_info_dict, myslice_filepath=slice_save_path)

        collate_info_dict = get_slice_results.collate_slice_info(slice_info_dict=slice_info_dict, collate_info_dict=collate_info_dict)
    
    collate_save_dirpath = get_path.get_collate_slice_savedir(commit_id=commit_id)
    collate_save_filepath = os.path.join(collate_save_dirpath, f"collate-"+slice_depth+config.SLICE_DOT_FILE_END)
    get_slice_results.get_slice_codes_from_info(slice_info_dict=collate_info_dict, myslice_filepath=collate_save_filepath)
    get_slice_results.save_collate_slice_info(collate_info_dict=collate_info_dict, collate_save_filepath=collate_save_filepath)

    pass