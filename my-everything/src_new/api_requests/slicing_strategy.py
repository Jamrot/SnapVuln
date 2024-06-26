import json
import os
import logging
from tqdm import tqdm
import time

import logging
logger = logging.getLogger(__name__)

import config.config as config
import api_requests.chatgpt_request as chatgpt_request
import api_requests.response_parser as response_parser
import utils.get_path as get_path


def get_SS_prompts(prompt_filepath, parsed_data, commit_id):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts[config.PROMPT_SLICING_STRATEGY]

    patch_summary = parsed_data.get("patch_summary", "")
    vulnerability_type = parsed_data.get("vulnerability_type", "")
    vulnerability_summary = parsed_data.get("vulnerability_summary", "")

    relevant_stmts = parsed_data.get("relevant_statements", "")
    patch_stmts = []
    for stmt in relevant_stmts:
        stmt_info = stmt.get("statement_info", "")
        stmt_code = stmt.get("statement", "")
        patch_stmts.append({
            'statement_info': stmt_info,
            'statement': stmt_code
        })

    patch_info = {
        'patch_summary': patch_summary,
        'vulnerability_type': vulnerability_type,
        'vulnerability_summary': vulnerability_summary,
        'relevant_statements': patch_stmts
    }

    # patch_info = parsed_data
    commit_clean_desc, commit_diff_code, commit_info = response_parser.get_patch(commit_id)
    patch_info["patch_summary"] = commit_clean_desc
    patch_info['diff_code'] = commit_diff_code

    messages = prompt_template
    messages[-1]['content'] = messages[-1]['content'].format(patch_info)

    return messages


def parse_SS_response(response_info):
    response_content = response_parser.get_response_content(response_info)
    response_dict = json.loads(response_content)
    # TODO: check if the response is in the correct format
    return response_dict


def save_SS_parsed(parsed_response, commit_id, stamp):
    parsed_savepath = get_path.get_parsed_data_savepath(commit_id=commit_id, level='function', stamp=stamp)+"-1.json"

    stmts_slicing_strategy = parsed_response.get("statements_slicing_strategy", "")

    parsed_data = response_parser.read_parsed(parsed_savepath=parsed_savepath)

    parsed_data["statements_slicing_strategy"] = stmts_slicing_strategy

    response_parser.save_parsed(parsed_data=parsed_data, parsed_savepath=parsed_savepath)

    return parsed_savepath


def do_slicing_strategy(commit_id, stamp):
    task = "SS"

    # get prompts
    parsed_save_path = get_path.get_parsed_data_savepath(commit_id=commit_id, level='function', stamp=stamp)
    parsed_data = response_parser.read_parsed(parsed_save_path)

    prompt_filepath = config.PROMPT_FILEPATH    
    messages = get_SS_prompts(prompt_filepath=prompt_filepath, parsed_data=parsed_data, commit_id=commit_id)
    
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
    parsed_response = parse_SS_response(response_info=response_info)
    parsed_filepath = get_path.get_parsed_response_filepath(task=task, commit_id=commit_id, timestamp=timestamp)
    response_parser.save_parsed_response(response_dict=parsed_response, parsed_filepath=parsed_filepath)

    # save parsed data
    parsed_save_path = save_SS_parsed(parsed_response=parsed_response, commit_id=commit_id, stamp=stamp)

    return parsed_save_path
