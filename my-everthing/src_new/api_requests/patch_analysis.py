import json
import os
import logging
from tqdm import tqdm
import time

import config.config as config
from api_requests.get_prompts import *
import api_requests.chatgpt_request as chatgpt_request
import utils.get_path as get_path


def get_PA_prompt(prompt_filepath, patch):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts['patch_analysis']

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
    response_content = chatgpt_request.get_response_content(response_info)
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


def save_PA_response(response_info, commit_id, request_content=""):
    response_dir = os.path.join(config.RESPONSE_DIR, 'PA')
    response_filename = get_path.get_response_filename(response_type='PA', commit_id=commit_id, parsed=False)
    response_filepath = os.path.join(response_dir, response_filename)
    chatgpt_request.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)


def save_PA_parsed_response(response_dict, commit_id):
    parsed_dir = os.path.join(config.PARSED_DIR, 'PA')
    if not os.path.exists(parsed_dir):
        os.makedirs(parsed_dir)
    parsed_filename = get_path.get_response_filename(response_type='PA', commit_id=commit_id, parsed=True)
    parsed_filepath = os.path.join(parsed_dir, parsed_filename)
    with open(parsed_filepath, 'w') as f:
        json.dump(response_dict, f, indent=2)


def test():
    commit_id = config.COMMIT_ID
    patch_desc, patch_diff_code, patch_info = chatgpt_request.get_patch(commit_id)

    prompt_filepath = config.PROMPT_FILEPATH
    patch = patch_desc+'\n'+patch_diff_code
    messages = get_PA_prompt(prompt_filepath=prompt_filepath, patch=patch)

    response_info, request_content = do_PA_request(messages)

    save_PA_response(response_info, commit_id=commit_id, request_content=request_content)

    response_dict = parse_PA_response(response_info)
    save_PA_parsed_response(response_dict, commit_id=commit_id)