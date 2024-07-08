import os
import config.config as config

import logging
logger = logging.getLogger(__name__)


def get_commit_id_short(commit_id):
    return commit_id[:7]


def get_save_rootpath(commit_id):
    commit_id_short = get_commit_id_short(commit_id=commit_id)
    save_root = os.path.join(config.DATA_ROOT, commit_id_short)
    if not os.path.exists(save_root):
        os.makedirs(save_root)
    return save_root

# src path
def get_src_relpath(modification:str, file_path_dict:dict):
    if modification=="ADD":
        src_relpath = os.path.join(config.NEW_CODE_DIRNAME, file_path_dict['new'])
    elif modification=="DELETE":
        src_relpath = os.path.join(config.OLD_CODE_DIRNAME, file_path_dict['old'])

    return src_relpath

# code path
def get_code_rootpath(save_root):
    code_root = os.path.join(save_root, config.CODE_ROOT_DIRNAME)
    if not os.path.exists(code_root):
        os.makedirs(code_root)
    return code_root


def get_code_savepath(code_root, src_relpath):
    code_savepath = os.path.join(code_root, src_relpath)
    # if not os.path.exists(code_savepath):
    #     os.makedirs(code_savepath)
    return code_savepath
    

# graph path
def get_graph_rootpath(save_root):
    graph_root = os.path.join(save_root, config.GRAPH_ROOT_DIRNAME)
    if not os.path.exists(graph_root):
        os.makedirs(graph_root)
    return graph_root


def get_graph_dirpath(graph_root, src_relpath):
    graph_dir = os.path.join(graph_root, src_relpath)
    if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
    return graph_dir


def get_graph_bin_filepath(graph_dir, code_basename, graph_level):
    bin_filepath = os.path.join(graph_dir, f"{config.GRAPH_START}-{graph_level}-{code_basename}.bin")
    return bin_filepath


def get_graph_dump_dirpath(graph_dir, bin_filepath, graph_dump_type):
    bin_filename = os.path.basename(bin_filepath)
    graph_dump_dirpath = os.path.join(graph_dir, "-".join([bin_filename, graph_dump_type]))
    return graph_dump_dirpath


def get_graph_savepath(graph_dir, code_basename, graph_type, graph_level):
    graph_save_name = f"{config.GRAPH_START}-{graph_level}-{code_basename}-{graph_type}{config.GRAPH_FILE_END}"
    graph_save_path = os.path.join(graph_dir, graph_save_name)
    
    return graph_save_path


# meta path
def get_meta_rootpath(save_root):
    meta_root = os.path.join(save_root, config.META_ROOT_DIRNAME)
    if not os.path.exists(meta_root):
        os.makedirs(meta_root)
    return meta_root


def get_mata_savepath(meta_root, src_relpath, code_basename="", funcname="", linenum=None, modification=None):
    meta_filename = f"{config.META_START}-{code_basename}-{funcname}-{linenum}-{modification}{config.META_FILE_END}"
    meta_dirpath = os.path.join(meta_root, src_relpath)
    if not os.path.exists(meta_dirpath):
        os.makedirs(meta_dirpath)
    meta_save_path = os.path.join(meta_dirpath, meta_filename)
    return meta_save_path


# slice path
def get_slice_rootpath(save_root):
    slice_root = os.path.join(save_root, config.SLICE_ROOT_DIRNAME)
    if not os.path.exists(slice_root):
        os.makedirs(slice_root)
    return slice_root

def get_slice_graph_savepath(slice_root, slice_direction, slice_graph, slice_level, code_basename="", funcname="", linenum=0):
    slice_save_name = f"{config.SLICE_START}-{slice_level}-{slice_direction}-{slice_graph}-{code_basename}-{funcname}-{linenum}{config.SLICE_DOT_FILE_END}"
    # TODO: choose the best slice save path
    slice_dirpath = os.path.join(slice_root, slice_level, code_basename, funcname, str(linenum), slice_direction, slice_graph)
    if not os.path.exists(slice_dirpath):
        os.makedirs(slice_dirpath)
    slice_save_path = os.path.join(slice_dirpath, slice_save_name)
    return slice_save_path


def get_collate_slice_savepath(slice_root, slice_depth):
    """return collate slice save path (DOT)"""
    collate_save_dir = os.path.join(slice_root, "collate")
    collate_filename = "-".join([config.SLICE_START, "collate", slice_depth])+config.SLICE_DOT_FILE_END    
    collate_savepath = os.path.join(collate_save_dir, collate_filename)
    if not os.path.exists(collate_save_dir):
        os.makedirs(collate_save_dir)
    return collate_savepath


def get_parsed_data_savepath(commit_id, level, stamp):
    save_root = get_save_rootpath(commit_id)
    commit_id_short = get_commit_id_short(commit_id)

    parsed_dirpath = os.path.join(save_root, "parsed", level+config.PARSED_DIR_END, config.REQUEST_MODEL)
    parsed_filename = "-".join([config.PARSED_START, commit_id_short, level, config.REQUEST_MODEL, stamp])+config.PARSED_FILE_END
    parsed_data_filepath = os.path.join(parsed_dirpath, parsed_filename)

    return parsed_data_filepath


def get_response_filepath(task, commit_id="", timestamp=None):
    if not timestamp:
        timestamp = config.CURRENT_TIME

    save_root = get_save_rootpath(commit_id)

    response_dir = os.path.join(save_root, "response", config.REQUEST_MODEL, timestamp)
    response_filename = f"response-{task}-{commit_id}-{config.REQUEST_MODEL}-{timestamp}.json"
    
    if not os.path.exists(response_dir):
        os.makedirs(response_dir)
    response_filepath = os.path.join(response_dir, response_filename)

    return response_filepath


def get_parsed_response_filepath(task, commit_id, timestamp=None):
    if not timestamp:
        timestamp = config.CURRENT_TIME

    save_root = get_save_rootpath(commit_id)

    response_dir = os.path.join(save_root, "response_parsed", config.REQUEST_MODEL, timestamp)
    response_filename = f"response_parsed-{task}-{commit_id}-{config.REQUEST_MODEL}-{timestamp}.json"
    
    if not os.path.exists(response_dir):
        os.makedirs(response_dir)
    response_filepath = os.path.join(response_dir, response_filename)

    return response_filepath