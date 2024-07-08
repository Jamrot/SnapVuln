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
import utils.get_path_new as get_path
import api_requests.response_parser as response_parser
import slices.get_slice_results as get_slice_results

import logging
logger = logging.getLogger(__name__)


def match_criterion_from_response(parsed_response, patch_stmts):
    matched_criterions = []

    criterions_dict = {}
    for patch_stmt in patch_stmts:
        file_path = patch_stmt['file_path']
        func_name = patch_stmt['func_name']
        stmt_info = patch_stmt['criterion']
        modification = patch_stmt['modification']
        criterion_info, _ = response_parser.get_line_info(file_path, func_name, stmt_info, modification)
        criterions_dict[criterion_info] = patch_stmt
    
    if "slicing_statements" in parsed_response:
        parsed_stmts = parsed_response['slicing_statements']
    elif "statements_slicing_strategy" in parsed_response:
        parsed_stmts = {stmt["statement_info"]:stmt for stmt in parsed_response['statements_slicing_strategy']}
    for stmt_id, parsed_stmt in parsed_stmts.items():
        stmt_info = parsed_stmt['statement_info']
        if stmt_info in criterions_dict:
            matched_criterion = criterions_dict[stmt_info]
            matched_criterion['direction'] = get_response_direction(parsed_stmt['slicing_direction'])
            matched_criterion['graph'] = get_response_graph_type(parsed_stmt['code_representation_graph'])
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


def build_graph(graph_dump_type, graph_dir, joern_parse_path, bin_filepath):
    graph_builder = GraphBuilder()
    
    if config.BIN_OVERWRITE or not os.path.exists(bin_filepath):
        graph_builder.joern_parse(source_path=joern_parse_path, bin_file=bin_filepath)
    
    graph_dump_dir = get_path.get_graph_dump_dirpath(graph_dir=graph_dir, bin_filepath=bin_filepath, graph_dump_type=graph_dump_type)
    if config.GRAPH_OVERWRITE or not os.path.exists(graph_dump_dir):
        graph_builder.joern_dump_graph(graph_dir=graph_dump_dir, bin_file=bin_filepath, graph_type=graph_dump_type)
    
    return graph_dump_dir


def add_filename(graph_type, graph_filename_savepath, graph_dir, bin_filepath):
    graph_type_filename = graph_type + "_filename"
    if os.path.exists(graph_filename_savepath) and not config.GRAPH_ALL_OVERWRITE:
        logging.warning(f"Graph with filename already exists and not overwrite: {graph_filename_savepath}")
        G_filename = nx.drawing.nx_agraph.read_dot(graph_filename_savepath)
        return G_filename

    # get graph_dump_filepath
    graph_dump_dir = get_path.get_graph_dump_dirpath(graph_dir=graph_dir, bin_filepath=bin_filepath, graph_dump_type=graph_type)
    graph_dump_filepath_dict = get_graph_dump_filepath(graph_dump_dir=graph_dump_dir, graph_type=graph_type)
    graph_dump_filepath = graph_dump_filepath_dict[graph_type]

    # read graph from graph_dump_filepath
    graph_builder = GraphBuilder()    
    G = graph_builder.read_graph(graph_dump_filepath)

    for node in G.nodes(data=True):
        node_id = node[0]
        node_data = node[1]
        
        # check if the node is a FILE or has FILENAME attribute
        node_label = node_data.get('label')
        node_filename = node_data.get('FILENAME')
        node_name = node_data.get('NAME')

        if node_label == "FILE" and node_name:
            G.nodes[node_id]['filename'] = node_name
        elif node_filename:
            G.nodes[node_id]['filename'] = node_filename
        else:
            for parent in G.predecessors(node_id):
                parent_data = G.nodes[parent]
                parent_label = parent_data.get('label')
                parent_filename = parent_data.get('FILENAME')
                parent_name = parent_data.get('NAME')

                if parent_label == "FILE" and parent_name:
                    G.nodes[node_id]['filename'] = parent_name
                    break
                elif parent_filename:
                    G.nodes[node_id]['filename'] = parent_filename
                    break
    
    # save graph to graph_filename_savepath
    graph_builder.save_graph(graph_filename_savepath, G)
    return G


def get_graph_dump_filepath(graph_dump_dir, graph_type, graph_level="file"):
    graph_dump_filepath_dict = {}

    if graph_type == "all":
        graph_dump_filepath_dict[graph_type] = os.path.join(graph_dump_dir, "export.dot")
    
    elif graph_type == "cpg":
        for root, dirs, files in os.walk(graph_dump_dir):
            for graph_dump_filename in files:
                if graph_dump_filename == "_global_.dot":
                    graph_file_filepath = os.path.join(root, graph_dump_filename)
                    file_filename = os.path.basename(root)
                    graph_dump_filepath_dict[file_filename] = graph_file_filepath
                    break
    else:
        logger.error(f"Cannot get graph_filepath, Invalid graph type: {graph_type}, please choose from ['all', 'cpg']")

    logger.info(f"Graph file path dict: {graph_dump_filepath_dict}")
    
    return graph_dump_filepath_dict


def build_single_slice(criterion_linenum, slice_direction, slice_graph, slice_depth, G_grpah=None, graph_save_path=None, slice_graph_savepath=None):
    
    if not G_grpah:
        if not graph_save_path:
            logger.error("[Slice build failed] Cannot find graph_save_path or G_grpah.")
            return None, None
        G_grpah = nx.drawing.nx_agraph.read_dot(graph_save_path)

    slicer = Slicer(G_graph=G_grpah)
    G_slice = slicer.build_slice(
        criterion_linenum=criterion_linenum,
        direction=slice_direction,
        g_type=slice_graph,
        depth=slice_depth)

    slicer.save_graph(
        G=G_slice,
        save_path=slice_graph_savepath)  
    
    return slice_graph_savepath, G_slice
    


def slice_from_strategy_seperate():
    # get patch stmts
    url = config.LINUX
    commit_id = config.COMMIT_ID
    save_root = get_path.get_save_rootpath(commit_id=commit_id)
    extractor = CriterionExtractor()
    patch_criterions = extractor.get_criteroin_from_patch(url=url, commit_id=commit_id)

    # save all patch stmts
    # all_meta_filepath = get_path.get_root_meta_filepath(commit_id=commit_id)
    # extractor._save_criterion_meta(criterions=patch_criterions, meta_filepath=all_meta_filepath)

    # match strategy
    parsed_filepath = config.PARSED_FILEPATH
    parsed_response = response_parser.read_parsed_response(response_filepath=parsed_filepath)
    matched_criterions = match_criterion_from_response(parsed_response, patch_criterions)
    extractor.save_criterion(criterions=matched_criterions)

    # build file level graph
    for criterion in matched_criterions:
        graph_type = "all"
        graph_level = "file" # function, file, module
        src_relpath = get_path.get_src_relpath(modification=criterion["modification"], file_path_dict=criterion["file_path"])
        funcname = criterion.get('func_name')
        code_basename = os.path.basename(src_relpath)
        
        graph_root = get_path.get_graph_rootpath(save_root=save_root)
        graph_dir = get_path.get_graph_dirpath(graph_root=graph_root, src_relpath=src_relpath)

        code_root = get_path.get_code_rootpath(save_root=save_root)
        joern_parse_path = get_path.get_code_savepath(code_root=code_root, src_relpath=src_relpath)
        bin_filepath = get_path.get_graph_bin_filepath(graph_dir=graph_dir, code_basename=code_basename, graph_level=graph_level)
        build_graph(
            graph_dump_type=graph_type, 
            graph_dir=graph_dir, 
            joern_parse_path=joern_parse_path, 
            bin_filepath=bin_filepath)

    # add filename
    G_name_dict = {}
    for criterion in matched_criterions:
        src_relpath = get_path.get_src_relpath(modification=criterion["modification"], file_path_dict=criterion["file_path"])
        code_basename = os.path.basename(src_relpath)

        graph_root = get_path.get_graph_rootpath(save_root=save_root)
        graph_dir = get_path.get_graph_dirpath(graph_root=graph_root, src_relpath=src_relpath)
        graph_save_path = get_path.get_graph_savepath(graph_dir=graph_dir, code_basename=code_basename, graph_type="all_filename", graph_level=graph_level)

        if graph_save_path not in G_name_dict:
            G_filename = add_filename(
                graph_type=graph_type,
                graph_filename_savepath=graph_save_path,
                graph_dir=graph_dir,
                bin_filepath=bin_filepath)
            G_name_dict[graph_save_path] = G_filename

    # build function level slice
    slice_root = get_path.get_slice_rootpath(save_root=save_root)
    collate_info_dict = {'code':{}, 'nodes':{}, 'edges':{}}
    for criterion in matched_criterions:
        src_relpath = get_path.get_src_relpath(modification=criterion["modification"], file_path_dict=criterion["file_path"])
        code_basename = os.path.basename(src_relpath)

        graph_root = get_path.get_graph_rootpath(save_root=save_root)
        graph_dir = get_path.get_graph_dirpath(graph_root=graph_root, src_relpath=src_relpath)
        graph_save_path = get_path.get_graph_savepath(graph_dir=graph_dir, code_basename=code_basename, graph_type="all_filename", graph_level=graph_level)

        G_name = G_name_dict[graph_save_path]

        criterion_linenum = criterion["criterion"]["line"]
        slice_direction = criterion["direction"]
        slice_graph = criterion["graph"]
        slice_depth = "function"
        
        funcname = criterion.get('func_name')
        slice_graph_savepath = get_path.get_slice_graph_savepath(slice_root=slice_root, slice_direction=slice_direction, slice_graph=slice_graph, slice_level=slice_depth, code_basename=code_basename, funcname=funcname, linenum=criterion_linenum)

        G_slice = build_single_slice(
            criterion_linenum=criterion_linenum,
            slice_direction=slice_direction,
            slice_graph=slice_graph,
            slice_depth=slice_depth,
            G_grpah=G_name,
            graph_save_path=graph_save_path,
            slice_graph_savepath=slice_graph_savepath)
        
        # save slice
        slice_info_dict = get_slice_results.get_slice_info_from_dot_criterion(criterion=criterion, myslice_filepath=slice_graph_savepath, level=slice_depth, G_slice=None)
        get_slice_results.get_slice_codes_json_from_info(slice_info_dict=slice_info_dict, myslice_filepath=slice_graph_savepath, commit_id=commit_id)
        get_slice_results.get_slice_codes_from_info(slice_info_dict=slice_info_dict, myslice_filepath=slice_graph_savepath, commit_id=commit_id)

        collate_info_dict = get_slice_results.collate_slice_info(slice_info_dict=slice_info_dict, collate_info_dict=collate_info_dict)
    
    collate_savepath = get_path.get_collate_slice_savepath(commit_id=commit_id, slice_depth=slice_depth)
    get_slice_results.get_slice_codes_json_from_info(slice_info_dict=collate_info_dict, myslice_filepath=collate_savepath, commit_id=commit_id)
    get_slice_results.get_slice_codes_from_info(slice_info_dict=collate_info_dict, myslice_filepath=collate_savepath, commit_id=commit_id)
    get_slice_results.save_collate_slice_info(collate_info_dict=collate_info_dict, collate_save_filepath=collate_savepath)


def slice_from_strategy(slice_depth, match_criterion, url=config.LINUX, commit_id=config.COMMIT_ID, parsed_filepath=config.PARSED_FILEPATH):
    # get patch stmts
    # url = config.LINUX
    # commit_id = config.COMMIT_ID
    save_root = get_path.get_save_rootpath(commit_id=commit_id)
    extractor = CriterionExtractor()
    patch_criterions = extractor.get_criteroin_from_patch(url=url, commit_id=commit_id)

    # match strategy
    # parsed_filepath = config.PARSED_FILEPATH
    parsed_response = response_parser.read_parsed_response(response_filepath=parsed_filepath)
    if match_criterion=="patch":
        matched_criterions = match_criterion_from_response(parsed_response, patch_criterions)
        extractor.save_criterion(criterions=matched_criterions)
    elif match_criterion=="response":
        matched_criterions = extractor.get_criterion_from_response(parsed_response=parsed_response, commit_id=commit_id)
    else:
        logger.error(f"Invalid match criterion: {match_criterion}")
        return

    G_name_dict = {}

    slice_root = get_path.get_slice_rootpath(save_root=save_root)
    collate_info_dict = {'code':{}, 'nodes':{}, 'edges':{}}

    # build file level graph
    for criterion in matched_criterions:
        graph_type = "all"
        graph_level = "file" if slice_depth=="function" else slice_depth # function, file, module
        src_relpath = get_path.get_src_relpath(modification=criterion["modification"], file_path_dict=criterion["file_path"])
        funcname = criterion.get('func_name')
        code_basename = os.path.basename(src_relpath)
        
        graph_root = get_path.get_graph_rootpath(save_root=save_root)
        graph_dir = get_path.get_graph_dirpath(graph_root=graph_root, src_relpath=src_relpath)

        code_root = get_path.get_code_rootpath(save_root=save_root)
        joern_parse_path = get_path.get_code_savepath(code_root=code_root, src_relpath=src_relpath)
        bin_filepath = get_path.get_graph_bin_filepath(graph_dir=graph_dir, code_basename=code_basename, graph_level=graph_level)
        build_graph(
            graph_dump_type=graph_type, 
            graph_dir=graph_dir, 
            joern_parse_path=joern_parse_path, 
            bin_filepath=bin_filepath)
        
        # add filename
        graph_save_path = get_path.get_graph_savepath(graph_dir=graph_dir, code_basename=code_basename, graph_type="all_filename", graph_level=graph_level)

        if graph_save_path not in G_name_dict:
            G_filename = add_filename(
                graph_type=graph_type,
                graph_filename_savepath=graph_save_path,
                graph_dir=graph_dir,
                bin_filepath=bin_filepath)
            G_name_dict[graph_save_path] = G_filename

        # build function level slice
        G_filename = G_name_dict[graph_save_path]

        criterion_linenum = criterion["criterion"]["line"]
        slice_direction = criterion["direction"]
        slice_graph = criterion["graph"]
        # slice_depth = "function"
        
        slice_graph_savepath = get_path.get_slice_graph_savepath(slice_root=slice_root, slice_direction=slice_direction, slice_graph=slice_graph, slice_level=slice_depth, code_basename=code_basename, funcname=funcname, linenum=criterion_linenum)

        G_slice = build_single_slice(
            criterion_linenum=criterion_linenum,
            slice_direction=slice_direction,
            slice_graph=slice_graph,
            slice_depth=slice_depth,
            G_grpah=G_filename,
            graph_save_path=graph_save_path,
            slice_graph_savepath=slice_graph_savepath)
        
        # save slice
        slice_info_dict = get_slice_results.get_slice_info_from_dot_criterion(criterion=criterion, myslice_filepath=slice_graph_savepath, level=slice_depth, G_slice=None)
        get_slice_results.get_slice_codes_json_from_info(slice_info_dict=slice_info_dict, myslice_filepath=slice_graph_savepath, commit_id=commit_id)
        get_slice_results.get_slice_codes_from_info(slice_info_dict=slice_info_dict, myslice_filepath=slice_graph_savepath, commit_id=commit_id)

        collate_info_dict = get_slice_results.collate_slice_info(slice_info_dict=slice_info_dict, collate_info_dict=collate_info_dict)
    
    collate_savepath = get_path.get_collate_slice_savepath(slice_root=slice_root, slice_depth=slice_depth)
    get_slice_results.get_slice_codes_json_from_info(slice_info_dict=collate_info_dict, myslice_filepath=collate_savepath, commit_id=commit_id)
    get_slice_results.get_slice_codes_from_info(slice_info_dict=collate_info_dict, myslice_filepath=collate_savepath, commit_id=commit_id)
    get_slice_results.save_collate_slice_info(collate_info_dict=collate_info_dict, collate_save_filepath=collate_savepath)