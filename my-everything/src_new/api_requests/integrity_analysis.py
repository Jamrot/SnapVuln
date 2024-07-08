import json
import os
import logging
from tqdm import tqdm
import time

import config.config as config
import api_requests.chatgpt_request as chatgpt_request
import api_requests.response_parser as response_parser
import utils.get_path_new as get_path

import logging
logger = logging.getLogger(__name__)


def get_IA_prompts(prompt_filepath, parsed_data, commit_id, slice_depth):
    # get patch information
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts[config.PROMPT_INTEGRITY_ANALYSIS]
    
    patch_summary = parsed_data.get("patch_summary", "")
    vulnerability_type = parsed_data.get("vulnerability_type", "")
    vulnerability_summary = parsed_data.get("vulnerability_summary", "")
    core_operations = [op['core_operation'] for op in parsed_data.get("core_operations", "")]

    commit_clean_desc, commit_diff_code, commit_info = response_parser.get_patch(commit_id)

    # get sliced code
    save_root = get_path.get_save_rootpath(commit_id=commit_id)
    slice_root = get_path.get_slice_rootpath(save_root=save_root)
    collate_slice_dotpath = get_path.get_collate_slice_savepath(slice_root=slice_root, slice_depth=slice_depth)
    collate_slice_jsonpath = collate_slice_dotpath.replace(config.SLICE_DOT_FILE_END, config.SLICE_CODE_FILE_END_JSON)
    with open(collate_slice_jsonpath, 'r') as f:
        collate_slice_json = json.load(f)
    
    patch_info = {
        'vulnerability_type': vulnerability_type,
        'vulnerability_type_summary': vulnerability_summary,
        # 'vulnerability_type_description': "A buffer overflow condition exists when a product attempts to put more data in a buffer than it can hold, or when it attempts to put data in a memory area outside of the boundaries of a buffer. The simplest type of error, and the most common cause of buffer overflows, is the \"classic\" case in which the product copies the buffer without restricting how much is copied. Other variants exist, but the existence of a classic overflow strongly suggests that the programmer is not considering even the most basic of security protections. ",
        'patch_summary': patch_summary,
        'diff_code': commit_diff_code,
        'core_operations': core_operations,
        'sliced_code': collate_slice_json
    }

    messages = prompt_template
    messages[-1]['content'] = messages[-1]['content'].format(patch_info)

    return messages


def parse_IA_response(response_info):
    response_content = response_parser.get_response_content(response_info)
    response_dict = json.loads(response_content)
    # TODO: check if the completeness judgement is consistent
    return response_dict


def save_IA_parsed(parsed_response, commit_id, stamp):
    parsed_savepath = get_path.get_parsed_data_savepath(commit_id=commit_id, level='function', stamp=stamp)
    parsed_data = response_parser.read_parsed(parsed_savepath=parsed_savepath)

    parsed_data['integrity_analysis'] = parsed_response
    # sliced_code_cause_vuln = parsed_data.get("sliced_code_cause_vulnerability", "")
    # includes_all_codes = sliced_code_cause_vuln.get("includes_all_codes", "")
    # justification_cause_vuln = sliced_code_cause_vuln.get("justification", "")

    # core_operation_codes = parsed_response.get("core_operation_codes", [])
    # includes_all_core_operations = core_operation_codes.get("includes_all_core_operations", "")
    # justifications_core_operation = core_operation_codes.get("justification", [])


    response_parser.save_parsed(parsed_data=parsed_data, parsed_savepath=parsed_savepath)

    return parsed_savepath


def do_integrity_analysis(commit_id, stamp, slice_depth):
    task = "integrity_analysis"

    # get prompts
    parsed_save_path = get_path.get_parsed_data_savepath(commit_id=commit_id, level=slice_depth, stamp=stamp)
    parsed_data = response_parser.read_parsed(parsed_save_path)

    prompt_filepath = config.PROMPT_FILEPATH
    messages = get_IA_prompts(prompt_filepath=prompt_filepath, parsed_data=parsed_data, commit_id=commit_id, slice_depth=slice_depth)

    # get response
    response_info, request_content = chatgpt_request.chatgpt_request(
        request_url=config.REQUEST_URL,
        api_key=config.OPENAI_API_KEY,
        model=config.REQUEST_MODEL,
        messages=messages
    )

    # save response
    timestamp = response_parser.get_response_timestamp(response_info=response_info)
    response_filepath = get_path.get_response_filepath(task=task, commit_id=commit_id, timestamp=stamp)
    response_parser.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)

    # save parsed response
    parsed_response = parse_IA_response(response_info=response_info)
    parsed_filepath = get_path.get_parsed_response_filepath(task=task, commit_id=commit_id, timestamp=stamp)
    response_parser.save_parsed_response(response_dict=parsed_response, parsed_filepath=parsed_filepath)

    # return parsed_filepath
    parsed_save_path = save_IA_parsed(parsed_response=parsed_response, commit_id=commit_id, stamp=stamp)

    return parsed_save_path
    