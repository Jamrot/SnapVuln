import os
import config

import logging
logger = logging.getLogger(__name__)

import log_config
log_config.setup_logging()

def get_save_root(commit_id):
    commit_id_short = get_commit_id_short
    save_root = os.path.join(config.DATA_ROOT, commit_id_short)

    return save_root

def get_criterion_savepath(commit_id, criterion):
    """get criterion save root, criterion dir, criterion code_file save_path, criterion module_dir save_path, criterion meta_data save_path"""
    save_root = get_save_root(commit_id=commit_id)

    commit_id_short = get_commit_id_short
    criterion_line = criterion['criterion']['line']
    file_code = criterion['file_code']
    file_code_old = file_code['old']
    file_code_new = file_code['new']
    commit_id = criterion['commit_id']
    func_name = criterion['func_name']
    file_path_old = criterion['file_path']['old']
    file_path_new = criterion['file_path']['new']

    criterion_dir = "-".join([commit_id_short, func_name, str(criterion_line)])
    # code file
    code_filename = "-".join([config.CODE_FILENAME_START, criterion_dir])+'.c'
    code_filepath = os.path.join(save_root, criterion_dir, code_filename)
    # module dir
    module_dir = os.path.dirname(file_path_old)
    module_dirname = "-".join([config.MODULE_DIRNAME_START, commit_id_short, "_".join(module_dir.split("/"))])
    module_dirpath = os.path.join(save_root, module_dirname)
    # meta file
    meta_filename = "-".join([config.META_FILENAME_START, criterion_dir])+'.json'
    meta_filepath = os.path.join(save_root, criterion_dir, meta_filename)

    return save_root, criterion_dir, code_filepath, module_dirpath, meta_filepath



def get_commit_id_short(commit_id):
    return commit_id[:7]


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


def get_and_check_bin_filepath(criterion, level, overwrite=False):
    graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
    filename_base = criterion.get('save_filename_base')
    module_path = criterion.get('save_module_dirpath')
    module_dirname = os.path.basename(module_path)
    if level=='module':
        bin_filepath = os.path.join(graph_dir, f"{level}-{module_dirname}.bin")
    else:
        bin_filepath = os.path.join(graph_dir, f"{level}-{filename_base}.bin")
    if os.path.exists(bin_filepath) and overwrite:
        logger.warning(f"removing bin file: {bin_filepath}")
        os.remove(bin_filepath)
    return bin_filepath


def get_graph_dump_dir(graph_dump_dir, graph_dump_type):
    graph_dump_dir = os.path.join(graph_dump_dir, "-".join([config.GRAPH_START, graph_dump_type]))
    return graph_dump_dir


def get_graph_save_filepath(criterion, graph_type, level):
    graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
    filename_base = criterion.get('save_filename_base')
    graph_save_path = os.path.join(graph_dir, "-".join([config.GRAPH_START, filename_base, graph_type+config.GRAPH_FILE_END]))
    return graph_save_path

def get_slice_save_filepath(criterion, direction, graph_type, depth):
    save_root = criterion.get('save_root')
    filename_base = criterion.get('save_filename_base')
    slice_dir = os.path.join(save_root, filename_base, filename_base+config.SLICE_DIR_END)    
    slice_save_path = os.path.join(slice_dir, direction, graph_type, depth, f"{config.SLICE_START}-{direction}_{graph_type}_{depth}-{filename_base}{config.SLICE_DOT_FILE_END}")

    return slice_save_path