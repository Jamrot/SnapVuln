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


def get_prompt(prompt_filepath, parsed_data, commit_id, slice_depth=""):
    # get patch information
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts[config.PROMPT_CORE_OPERATIONS]
    
    patch_summary = parsed_data.get("patch_summary", "")
    vulnerability_type = parsed_data.get("vulnerability_type", "")
    vulnerability_summary = parsed_data.get("vulnerability_summary", "")

    commit_clean_desc, commit_diff_code, commit_info = response_parser.get_patch(commit_id)
    
    patch_info = {
        # 'patch_summary': patch_summary,
        'vulnerability_type': vulnerability_type,
        'vulnerability_summary': vulnerability_summary,
        # 'diff_code': commit_diff_code,
        # 'sliced_code': collate_slice_json
    }

    messages = prompt_template
    messages[-1]['content'] = messages[-1]['content'].format(patch_info)

    return messages


def parse_response(response_info):
    response_content = response_parser.get_response_content(response_info)
    response_dict = json.loads(response_content)
    return response_dict


def save_parsed(parsed_response, commit_id, stamp):
    parsed_savepath = get_path.get_parsed_data_savepath(commit_id=commit_id, level='function', stamp=stamp)
    parsed_data = response_parser.read_parsed(parsed_savepath=parsed_savepath)

    core_operations = parsed_response.get("core_operations", [])
    if not core_operations:
        logger.error("No core operations found in the response.")
        return parsed_savepath

    parsed_data["core_operations"] = core_operations
    # for core_operation_dict in core_operations:
    #     core_operation, justification = core_operation_dict.get("core_operation", ""), core_operation_dict.get("justification", "")
    #     parsed_data["core_operations"].append(core_operation)

    response_parser.save_parsed(parsed_data=parsed_data, parsed_savepath=parsed_savepath)

    return parsed_savepath


def do_core_operations(commit_id, stamp, slice_depth):
    task = "core_operations"

    # get prompts
    # parsed_save_path = get_path.get_parsed_data_savepath(commit_id=commit_id, level=slice_depth, stamp=stamp)
    parsed_save_path = config.PARSED_FILEPATH
    parsed_data = response_parser.read_parsed(parsed_save_path)

    prompt_filepath = config.PROMPT_FILEPATH
    messages = get_prompt(prompt_filepath=prompt_filepath, parsed_data=parsed_data, commit_id=commit_id, slice_depth=slice_depth)

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
    parsed_response = parse_response(response_info=response_info)
    parsed_filepath = get_path.get_parsed_response_filepath(task=task, commit_id=commit_id, timestamp=stamp)
    response_parser.save_parsed_response(response_dict=parsed_response, parsed_filepath=parsed_filepath)

    # return parsed_filepath
    parsed_save_path = save_parsed(parsed_response=parsed_response, commit_id=commit_id, stamp=stamp)

    return parsed_save_path
    