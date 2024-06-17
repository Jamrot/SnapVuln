import json
import os
import logging
from tqdm import tqdm
import time

import logging
logger = logging.getLogger(__name__)

import config.config as config
from api_requests.get_prompts import *
import api_requests.chatgpt_request as chatgpt_request
import utils.get_path as get_path
import utils.read_file as read_file


def get_SS_prompts_1(prompt_filepath, parsed_response, commit_diff_code):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts['slicing_strategy']

    messages = prompt_template
    parsed_response = json.loads(parsed_response)

    patch_info = parsed_response
    patch_info['related_code'] = commit_diff_code

    messages[-1]['content'] = messages[-1]['content'].format(patch_info)

    return messages


def get_SS_prompts(prompt_filepath, parsed_response, commit_diff_code):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts['slicing_strategy_stmt']

    messages = prompt_template
    # parsed_response = json.loads(parsed_response)

    patch_info = parsed_response
    patch_info['related_code'] = commit_diff_code

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
    response_content = chatgpt_request.get_response_content(response_info)
    response_content = response_content.replace('```json', '').strip("```")
    response_dict = json.loads(response_content)
    # TODO: check if the response is in the correct format
    return response_dict


def save_SS_response(response_info, commit_id, request_content=""):
    response_dir = os.path.join(config.RESPONSE_DIR, 'SS')
    response_filename = get_path.get_response_filename(response_type='SS', commit_id=commit_id, parsed=False)
    response_filepath = os.path.join(response_dir, response_filename)
    chatgpt_request.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)


def save_SS_parse(response_dict, commit_id):
    parsed_dir = os.path.join(config.PARSED_DIR, 'SS')
    if not os.path.exists(parsed_dir):
        os.makedirs(parsed_dir)
    parsed_filename = get_path.get_response_filename(response_type='SS', commit_id=commit_id, parsed=True)
    parsed_filepath = os.path.join(parsed_dir, parsed_filename)
    with open(parsed_filepath, 'w') as f:
        json.dump(response_dict, f, indent=2)


def read_parsed_response(filepath):
    with open(filepath, 'r') as f:
        parsed_response = json.load(f)
    return parsed_response


def test():
    commit_id = config.COMMIT_ID
    # filepath_PA = "my-everthing/responses/parsed/PA/parsed_PA-a282a2f-20240617053613.json"
    # filepath_SE = "my-everthing/responses/parsed/SE/parsed_SE-a282a2f-20240617073944.json"
    # parsed_response = read_parsed_response(filepath_PA)
    # parsed_response_SE = read_parsed_response(filepath_SE)
    # parsed_response.update(parsed_response_SE)

    # prompt_filepath = config.PROMPT_FILEPATH    
    # patch_desc, patch_diff_code, patch_info = chatgpt_request.get_patch(commit_id)
    # messages = get_SS_prompts(prompt_filepath=prompt_filepath, parsed_response=parsed_response, commit_diff_code=patch_diff_code)

    # response_info, request_content = do_SS_request(messages)

    # save_SS_response(response_info=response_info, commit_id=commit_id, request_content=request_content)

    filepath = "my-everthing/responses/original/SS/response_SS-a282a2f-20240617093141.json"
    response_info = read_file.read_response_info(response_filepath=filepath)
    response_SS = parse_SS_response(response_info)
    save_SS_parse(response_dict=response_SS, commit_id=commit_id)
