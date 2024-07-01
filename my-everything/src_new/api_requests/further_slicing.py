import json
import os
import logging
from tqdm import tqdm
import time

import config.config as config
import api_requests.chatgpt_request as chatgpt_request
import api_requests.response_parser as response_parser
import utils.get_path as get_path

import logging
logger = logging.getLogger(__name__)


def get_prompts(prompt_filepath, parsed_data, commit_id, slice_depth=""):
    # get patch information
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts[config.PROMPT_FURTHER_SLICING]
    
    patch_summary = parsed_data.get("patch_summary", "")
    vulnerability_type = parsed_data.get("vulnerability_type", "")
    vulnerability_summary = parsed_data.get("vulnerability_summary", "")

    commit_clean_desc, commit_diff_code, commit_info = response_parser.get_patch(commit_id)

    # get sliced code
    collate_slice_dotpath = get_path.get_collate_slice_savepath(commit_id=commit_id, slice_depth=slice_depth)
    collate_slice_jsonpath = collate_slice_dotpath.replace(config.SLICE_DOT_FILE_END, config.SLICE_CODE_FILE_END_JSON)
    with open(collate_slice_jsonpath, 'r') as f:
        collate_slice_json = json.load(f)
    
    # get completeness judgement
    integrity_analysis = parsed_data.get("integrity_analysis", {})
    contains_all_relevant_code = integrity_analysis.get("final_determination", {}).get("contains_all_relevant_code", "")
    includes_cause_codes = integrity_analysis.get("sliced_code_cause_vulnerability", {}).get("includes_all_codes", "")
    includes_all_core_operations = integrity_analysis.get("sliced_code_core_operations", {}).get("includes_all_core_operations", "")
    operation_list = integrity_analysis.get("sliced_code_core_operations", {}).get("core_operation_codes", [])

    missed_operations = []
    included_operations = []
    for operation_dict in operation_list:
        operation = operation_dict.get("core_operation", "")
        operation_code = operation_dict.get("sliced_code", "")
        if operation_code=="NONE":
            missed_operations.append(operation)
        else:
            included_operations.append(operation)
    
    # TODO: check if the completeness judgement is consistent
    completeness_judgement = {
        'contains_all_relevant_code': contains_all_relevant_code,
        'includes_cause_codes': includes_cause_codes,
        'includes_all_core_operations': includes_all_core_operations,
        'missed_operations': missed_operations,
        'included_operations': included_operations
    }


    patch_info = {
        'vulnerability_type': vulnerability_type,
        'vulnerability_summary': vulnerability_summary,
        'patch_summary': patch_summary,
        'diff_code': commit_diff_code,
        'sliced_code': collate_slice_json,
        'completeness_judgement': completeness_judgement
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

    further_slicing = parsed_response.get("statements_slicing_strategy", [])
    if not further_slicing:
        logger.error("No further slicing found in the response.")
        return parsed_savepath

    parsed_data["further_slicing"] = further_slicing
    return response_parser.save_parsed(parsed_data, parsed_savepath)


def do_analysis(commit_id, stamp, slice_depth):
    task = "further_slicing"

    # get prompts
    parsed_save_path = get_path.get_parsed_data_savepath(commit_id=commit_id, level=slice_depth, stamp=stamp)
    parsed_data = response_parser.read_parsed(parsed_save_path)

    prompt_filepath = config.PROMPT_FILEPATH
    messages = get_prompts(prompt_filepath=prompt_filepath, parsed_data=parsed_data, commit_id=commit_id, slice_depth=slice_depth)

    # get response
    response_info, request_content = chatgpt_request.chatgpt_request(
        request_url=config.REQUEST_URL,
        api_key=config.OPENAI_API_KEY,
        model=config.REQUEST_MODEL,
        messages=messages
    )

    # save response
    timestamp = response_parser.get_response_timestamp(response_info=response_info)
    response_filepath = get_path.get_response_filepath(task=task, commit_id=commit_id, timestamp=timestamp)
    response_parser.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)

    # save parsed response
    parsed_response = parse_response(response_info=response_info)
    parsed_filepath = get_path.get_parsed_response_filepath(task=task, commit_id=commit_id, timestamp=timestamp)
    response_parser.save_parsed_response(response_dict=parsed_response, parsed_filepath=parsed_filepath)

    # return parsed_filepath
    parsed_save_path = save_parsed(parsed_response=parsed_response, commit_id=commit_id, stamp=stamp)

    return parsed_save_path