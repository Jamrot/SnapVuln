import json
import os
import logging
from tqdm import tqdm
import time

import config.config as config
import api_requests.chatgpt_request as chatgpt_request
import api_requests.response_parser as response_parser
import utils.get_path as get_path


def get_PA_prompt(prompt_filepath, commit_id):
    # get prompt template
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    prompt_template = all_prompts['patch_analysis']

    # get patch to fill the prompt template
    patch_desc, patch_diff_code, patch_info = response_parser.get_patch(commit_id)
    patch = patch_desc+'\n'+patch_diff_code

    messages = prompt_template
    messages[-1]['content'] = messages[-1]['content'].format(patch)

    return messages


def do_PA_request(messages):
    response_info, request_content = chatgpt_request.chatgpt_request(
        request_url=config.REQUEST_URL,
        api_key=config.OPENAI_API_KEY,
        model=config.REQUEST_MODEL,
        messages=messages
    )

    return response_info, request_content


def parse_PA_response(response_info):
    response_content = response_parser.get_response_content(response_info)
    response_dict = json.loads(response_content)

    # check if the response is in the correct format
    patch_summary = response_dict.get("patch_summary", "")
    vulnerability_type = response_dict.get("vulnerability_type", "")
    vulnerability_summary = response_dict.get("vulnerability_summary", "")

    if not patch_summary:
        logging.error("Failed to get patch summary from response.")
    if not vulnerability_type:
        logging.error("Failed to get vulnerability type from response.")
    if not vulnerability_summary:
        logging.error("Failed to get vulnerability summary from response.")
    
    return response_dict


def save_PA_response(response_info, commit_id, request_content="", timestamp=None):
    task = "PA"
    response_dir = os.path.join(config.RESPONSE_DIR, task)
    response_filename = get_path.get_response_filename(task=task, commit_id=commit_id, parsed=False, timestamp=timestamp)
    response_filepath = os.path.join(response_dir, response_filename)
    response_parser.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)


def save_PA_parsed_response(response_dict, commit_id, timestamp=None):
    task = "PA"
    parsed_dir = os.path.join(config.PARSED_DIR, task)
    if not os.path.exists(parsed_dir):
        os.makedirs(parsed_dir)
    parsed_filename = get_path.get_response_filename(task=task, commit_id=commit_id, parsed=True, timestamp=timestamp)
    parsed_filepath = os.path.join(parsed_dir, parsed_filename)
    with open(parsed_filepath, 'w') as f:
        json.dump(response_dict, f, indent=2)

    return parsed_filepath


def do_patch_analysis(commit_id):
    prompt_filepath = config.PROMPT_FILEPATH

    messages = get_PA_prompt(prompt_filepath=prompt_filepath, commit_id=commit_id)

    response_info, request_content = do_PA_request(messages)
    save_PA_response(response_info=response_info, commit_id=commit_id, request_content=request_content)

    response_dict = parse_PA_response(response_info=response_info)
    filepath_PA = save_PA_parsed_response(response_dict, commit_id=commit_id)

    return filepath_PA


def test():
    commit_id = config.COMMIT_ID
    
    prompt_filepath = config.PROMPT_FILEPATH
    
    messages = get_PA_prompt(prompt_filepath=prompt_filepath, commit_id=commit_id)

    response_info, request_content = do_PA_request(messages)
    timestamp = response_parser.get_response_timestamp(response_info=response_info)
    save_PA_response(response_info=response_info, commit_id=commit_id, request_content=request_content, timestamp=timestamp)

    response_dict = parse_PA_response(response_info=response_info, timestamp=timestamp)
    save_PA_parsed_response(response_dict, commit_id=commit_id)