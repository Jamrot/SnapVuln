import config.config as config
import os
import json
import datetime

import logging
logger = logging.getLogger(__name__)

from analysis.patch_analyzer import PatchAnalyzer
import utils.get_path as get_path


def read_parsed_response(response_filepath):
    with open(response_filepath, 'r') as f:
        response = json.load(f)
    return response


def read_single_response(response_filepath):
    with open(response_filepath, 'r') as f:
        response_json = json.load(f)
    
    response = response_json['response']['choices'][0]['message']['content']
    return response


def read_response_info(response_filepath):
    with open(response_filepath, 'r') as f:
        response_json = json.load(f)
    response_info = response_json['response']
    return response_info


def get_response_content(response_info):
    response_content = response_info['choices'][0]['message']['content']
    response_content = response_content.replace('```json', '').strip("```")
    return response_content


def get_response_timestamp(response_info):
    timestamp = response_info.get("created")
    if not timestamp:
        timestamp = 'N'+datetime.datetime.now().timestamp()
    dt = datetime.datetime.fromtimestamp(timestamp)
    timestamp_str = dt.strftime('%Y%m%d%H%M%S')
    return timestamp_str


def save_response(response, response_filepath, request_content=""):
    save_content = {
        "request": request_content,
        "response": response        
    }
    save_dir = os.path.dirname(response_filepath)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(response_filepath, 'w') as f:
        json.dump(save_content, f, indent=2)


def save_parsed_response(response_dict, parsed_filepath):
    save_dir = os.path.dirname(parsed_filepath)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(parsed_filepath, 'w') as f:
        json.dump(response_dict, f, indent=2)
    return parsed_filepath


def get_patch(commit_id):
    patch_analyzer = PatchAnalyzer(url=config.LINUX, commit_id=commit_id)
    _, clean_desc = patch_analyzer.get_description()
    diff_code = patch_analyzer.get_diff_code()
    info = patch_analyzer.get_commit_info()
    return clean_desc, diff_code, info


def get_line_info(file_path, func_name, stmt_info, modification):
    file_path_old = file_path['old']
    file_path_new = file_path['new']
    line = stmt_info['line']
    code = stmt_info['code']
    # line_info = " | ".join([
    #     "old_path: "+file_path_old, 
    #     "new_path: "+file_path_new, 
    #     "function: "+func_name, 
    #     "line_num: "+str(line), 
    #     "modification: "+modification])

    line_info = " | ".join([file_path_old, func_name, str(line), modification])

    return line_info, code


def read_parsed(parsed_savepath):
    if not os.path.exists(parsed_savepath):
        parsed = {}
        return parsed
    with open(parsed_savepath, 'r') as f:
        parsed = json.load(f)
    return parsed

def save_parsed(parsed_data, parsed_savepath):
    save_dir = os.path.dirname(parsed_savepath)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(parsed_savepath, 'w') as f:
        json.dump(parsed_data, f, indent=2)
    return parsed_savepath


def sort_parsed(parsed_data):
    patch_summary = parsed_data.get("patch_summary", "")
    vulnerability_type = parsed_data.get("vulnerability_type", "")
    vulnerability_summary = parsed_data.get("vulnerability_summary", "")
    relevant_stmts = parsed_data.get("relevant_statements", "")
    stmts_slicing_strategy = parsed_data.get("statements_slicing_strategy", "")

    selected_stmts = {}
    for stmt in relevant_stmts:
        stmt_info = stmt.get("statement_info", "")
        stmt_code = stmt.get("statement", "")
        reason = stmt.get("reason", "")
        selected_stmts[stmt_info] = {
            'statement_info': stmt_info,
            'statement': stmt_code,
            'reason': reason
        }

    for stmt in stmts_slicing_strategy:
        stmt_info = stmt.get("statement_info", "")
        stmt_code = stmt.get("statement", "")
        direction = stmt.get("slicing_direction", "")
        graph = stmt.get("code_representation_graph", "")
        justification = stmt.get("justification", "")

        if stmt_info not in selected_stmts:
            logger.error(f"stmt_info {stmt_info} not found in statements extraction results.")
            continue
        if selected_stmts[stmt_info]['statement'] != stmt_code:
            logger.error(f"stmt_code mismatch for stmt_info {stmt_info}.")
        
        selected_stmts[stmt_info]['slicing_direction'] = direction
        selected_stmts[stmt_info]['code_representation_graph'] = graph
        selected_stmts[stmt_info]['justification'] = justification
    
    sorted_parsed_data = {
        "patch_summary": patch_summary,
        "vulnerability_type": vulnerability_type,
        "vulnerability_summary": vulnerability_summary,
        "slicing_statements": selected_stmts
    }
    
    return sorted_parsed_data


def do_sort_parsed(parsed_savepath):
    parsed_filename = os.path.basename(parsed_savepath)
    parsed_dir = os.path.dirname(parsed_savepath)
    sorted_parsed_filename = f"sorted_{parsed_filename}"
    sorted_parsed_savepath = os.path.join(parsed_dir, sorted_parsed_filename)
    parsed_data = read_parsed(parsed_savepath)
    sorted_parsed_data = sort_parsed(parsed_data)
    save_parsed_response(sorted_parsed_data, sorted_parsed_savepath)