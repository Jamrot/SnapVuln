import os
import config.config as config

import logging
logger = logging.getLogger(__name__)

def get_commit_id_short(commit_id):
    return commit_id[:7]


def get_save_root(commit_id):
    commit_id_short = get_commit_id_short(commit_id=commit_id)
    save_root = os.path.join(config.DATA_ROOT, commit_id_short)
    if not os.path.exists(save_root):
        os.makedirs(save_root)
    return save_root


def get_criterion_savepath(commit_id, criterion):
    """get criterion save root, criterion dir, criterion code_file save_path, criterion module_dir save_path, criterion meta_data save_path"""
    save_root = get_save_root(commit_id=commit_id)

    commit_id_short = get_commit_id_short(commit_id=commit_id)
    criterion_line = criterion['criterion']['line']
    file_code = criterion['file_code']
    file_code_old = file_code['old']
    file_code_new = file_code['new']
    commit_id = criterion['commit_id']
    func_name = criterion['func_name']
    file_path_old = criterion['file_path']['old']
    file_path_new = criterion['file_path']['new']

    basename = "-".join([commit_id_short, func_name, str(criterion_line)])
    criterion_dir_path = os.path.join(save_root, basename)
    if not os.path.exists(criterion_dir_path):
        os.makedirs(criterion_dir_path)
    # module dir
    module_dir = os.path.dirname(file_path_old)
    module_dirpath = os.path.join(save_root, config.CODE_DIRNAME, module_dir)
    # code file
    code_filename = os.path.basename(file_path_old)
    code_filepath = os.path.join(module_dirpath, code_filename)
    # meta file
    meta_filename = "-".join([config.META_FILENAME_START, basename])+'.json'
    meta_filepath = os.path.join(criterion_dir_path, meta_filename)

    return save_root, basename, code_filepath, module_dirpath, meta_filepath


def get_graph_dir_from_criterion(criterion, level):
    filename_base = criterion.get('save_filename_base')
    save_root = criterion.get('save_root')
    module_path = criterion.get('save_module_dirpath')
    module_dirname = os.path.basename(module_path)
    # if level=="module":
    #     graph_dir = os.path.join(save_root, module_dirname+config.GRAPH_DIR_END)        
    # else:
    #     graph_dir = os.path.join(save_root, filename_base, filename_base+config.GRAPH_DIR_END)  

    file_path_old = criterion['file_path']['old']
    module_dir = os.path.dirname(file_path_old)
    graph_dir = os.path.join(save_root, config.GRAPH_DIRNAME, module_dir)
    return graph_dir


def get_joern_parse_path_from_criterion(criterion, level):
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


def get_bin_filepath_from_criterion(criterion, level):
    graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
    filename_base = criterion.get('save_filename_base')
    module_path = criterion.get('save_module_dirpath')
    module_dirname = os.path.basename(module_path)
    code_filename = os.path.basename(criterion.get('save_file_code_old_filepath'))
    if level=='module':
        bin_filepath = os.path.join(graph_dir, f"{level}-{module_dirname}.bin")
    else:
        bin_filepath = os.path.join(graph_dir, f"{level}-{code_filename}.bin")

    return bin_filepath


def get_graph_dump_dir(graph_dump_dir, bin_filepath, graph_dump_type):
    bin_filename = os.path.basename(bin_filepath)
    graph_dump_dir = os.path.join(graph_dump_dir, "-".join([config.GRAPH_START, bin_filename, graph_dump_type]))
    return graph_dump_dir


def get_graph_savepath_from_criterion(criterion, graph_type, level):
    graph_dir = get_graph_dir_from_criterion(criterion=criterion, level=level)
    filename_base = criterion.get('save_filename_base')
    # graph_save_path = os.path.join(graph_dir, "-".join([config.GRAPH_START, filename_base, graph_type+config.GRAPH_FILE_END]))
    module_path = criterion.get('save_module_dirpath')
    module_dirname = os.path.basename(module_path)
    code_filename = os.path.basename(criterion.get('save_file_code_old_filepath'))
    if level=='module':
        graph_save_path = os.path.join(graph_dir, "-".join([config.GRAPH_START, module_dirname, graph_type+config.GRAPH_FILE_END]))
    else:
        graph_save_path = os.path.join(graph_dir, "-".join([config.GRAPH_START, code_filename, graph_type+config.GRAPH_FILE_END]))
    
    return graph_save_path


def get_slice_savepath_from_criterion(criterion, direction, graph_type, depth):
    save_root = criterion.get('save_root')
    filename_base = criterion.get('save_filename_base')
    slice_dir = os.path.join(save_root, filename_base, filename_base+config.SLICE_DIR_END)    
    slice_save_path = os.path.join(slice_dir, direction, graph_type, depth, f"{config.SLICE_START}-{direction}_{graph_type}_{depth}-{filename_base}{config.SLICE_DOT_FILE_END}")

    return slice_save_path


def get_collate_slice_savedir(commit_id):
    save_root = get_save_root(commit_id=commit_id)
    collate_save_dir = os.path.join(save_root,"collate"+config.SLICE_DIR_END)
    if not os.path.exists(collate_save_dir):
        os.makedirs(collate_save_dir)
    return collate_save_dir


def get_code_filepath_list_from_criterion(criterion, level='function')->list:
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

    return filepath_list


def get_response_filepath(task, commit_id="", timestamp=None):
    if not timestamp:
        timestamp = config.CURRENT_TIME

    commit_id = get_commit_id_short(commit_id)
    response_filename = f"response_{task}-{commit_id}-{timestamp}.json"
    
    response_dir = os.path.join(config.RESPONSE_DIR, task)
    if not os.path.exists(response_dir):
        os.makedirs(response_dir)
    response_filepath = os.path.join(response_dir, response_filename)

    return response_filepath


def get_parsed_response_filepath(task, commit_id, timestamp=None):
    if not timestamp:
        timestamp = config.CURRENT_TIME

    commit_id = get_commit_id_short(commit_id)
    parsed_response_filename = f"parsed_{task}-{commit_id}-{timestamp}.json"
    
    parsed_dir = os.path.join(config.PARSED_DIR, commit_id, task)
    if not os.path.exists(parsed_dir):
        os.makedirs(parsed_dir)
    parsed_response_filepath = os.path.join(parsed_dir, parsed_response_filename)

    return parsed_response_filepath


def get_parsed_data_savepath(commit_id, level, stamp):
    save_root = get_save_root(commit_id)
    commit_id_short = get_commit_id_short(commit_id)

    parsed_dirpath = os.path.join(save_root, "parsed", level+config.PARSED_DIR_END, config.REQUEST_MODEL)
    parsed_filename = "-".join([config.PARSED_START, commit_id_short, level, config.REQUEST_MODEL, stamp])+config.PARSED_FILE_END
    parsed_data_filepath = os.path.join(parsed_dirpath, parsed_filename)

    return parsed_data_filepath