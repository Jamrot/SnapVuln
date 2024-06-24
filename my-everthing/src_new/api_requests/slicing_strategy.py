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


def get_SS_prompts(prompt_filepath, parsed_response, commit_id):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts[config.PROMPT_SLICING_STRATEGY]

    patch_info = parsed_response
    _, commit_diff_code, _ = response_parser.get_patch(commit_id)
    patch_info['related_code'] = commit_diff_code

    messages = prompt_template
    messages[-1]['content'] = messages[-1]['content'].format(patch_info)

    return messages


def do_SS_request(messages):
    response_info, request_content = chatgpt_request.chatgpt_request(
        request_url=config.REQUEST_URL,
        api_key=config.OPENAI_API_KEY,
        model=config.REQUEST_MODEL,
        messages=messages
    )

    return response_info, request_content


def parse_SS_response(response_info):
    response_content = response_parser.get_response_content(response_info)
    response_dict = json.loads(response_content)
    # TODO: check if the response is in the correct format
    return response_dict


def save_SS_response(response_info, commit_id, request_content=""):
    task = 'SS'
    response_dir = os.path.join(config.RESPONSE_DIR, task)
    response_filename = get_path.get_response_filename(task=task, commit_id=commit_id, parsed=False)
    response_filepath = os.path.join(response_dir, response_filename)
    response_parser.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)


def save_SS_parse(response_dict, commit_id):
    task = 'SS'
    parsed_dir = os.path.join(config.PARSED_DIR, task)
    if not os.path.exists(parsed_dir):
        os.makedirs(parsed_dir)
    parsed_filename = get_path.get_response_filename(task=task, commit_id=commit_id, parsed=True)
    parsed_filepath = os.path.join(parsed_dir, parsed_filename)
    with open(parsed_filepath, 'w') as f:
        json.dump(response_dict, f, indent=2)


def save_SS_parsed(parsed_response, commit_id, stamp):
    parsed_savepath = get_path.get_parsed_savepath_from_criterion(commit_id=commit_id, level='function', stamp=stamp)

    stmt_info = parsed_response.get("statement_info", "")
    statement = parsed_response.get("statement", "")
    slicing_direction = parsed_response.get("slicing_direction", "")
    slicing_graph = parsed_response.get("code_representation_graph", "")
    reason = parsed_response.get("justification", "")

    parsed_data = response_parser.read_parsed(parsed_savepath=parsed_savepath)

    parsed_data["SS_statement_info"] = stmt_info
    parsed_data["SS_statement"] = statement
    parsed_data["SS_slicing_direction"] = slicing_direction
    parsed_data["SS_code_representation_graph"] = slicing_graph
    parsed_data["SS_reason"] = reason

    response_parser.save_parsed(parsed_data=parsed_data, parsed_savepath=parsed_savepath)

    return parsed_savepath


def do_slicing_strategy(commit_id, filepath_PA, filepath_SE):
    task = "SS"

    # get prompts
    parsed_response = response_parser.read_parsed_response(filepath_PA)
    parsed_response_SE = response_parser.read_parsed_response(filepath_SE)
    parsed_response.update(parsed_response_SE)

    prompt_filepath = config.PROMPT_FILEPATH    
    messages = get_SS_prompts(prompt_filepath=prompt_filepath, parsed_response=parsed_response, commit_id=commit_id)
    
    # get response
    response_info, request_content = do_SS_request(messages)

    # save response
    timestamp = response_parser.get_response_timestamp(response_info=response_info)
    response_filepath = get_path.get_response_filepath(task=task, commit_id=commit_id, timestamp=timestamp)
    response_parser.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)

    # save parsed response
    parsed_response = parse_SS_response(response_info=response_info)
    parsed_filepath = get_path.get_parsed_filepath(task=task, commit_id=commit_id, timestamp=timestamp)
    response_parser.save_parsed_response(response_dict=parsed_response, parsed_filepath=parsed_filepath)

    return parsed_filepath
