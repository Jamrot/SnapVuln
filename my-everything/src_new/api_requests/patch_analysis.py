import json
import os
import logging
from tqdm import tqdm
import time

import config.config as config
import api_requests.chatgpt_request as chatgpt_request
import api_requests.response_parser as response_parser
import utils.get_path_new as get_path


def get_PA_prompt(prompt_filepath, commit_id):
    # get prompt template
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    prompt_template = all_prompts[config.PROMPT_PATCH_ANALYSIS]

    # get patch to fill the prompt template
    patch_desc, patch_diff_code, patch_info = response_parser.get_patch(commit_id)
    patch = patch_desc+'\n'+patch_diff_code
    patch_dumps = json.dumps(patch)

    messages = prompt_template
    messages[-1]['content'] = messages[-1]['content'].format(patch_dumps)

    return messages


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


def save_PA_parsed(parsed_response, parsed_savepath):
    patch_summary = parsed_response.get("patch_summary", "")
    vulnerability_type = parsed_response.get("vulnerability_type", "")
    vulnerability_summary = parsed_response.get("vulnerability_summary", "")

    parsed_data = response_parser.read_parsed(parsed_savepath=parsed_savepath)
    parsed_data["patch_summary"] = patch_summary
    parsed_data["vulnerability_type"] = vulnerability_type
    parsed_data["vulnerability_summary"] = vulnerability_summary

    response_parser.save_parsed(parsed_data=parsed_data, parsed_savepath=parsed_savepath)


def do_patch_analysis(commit_id, stamp=None):
    task = "patch_analysis"  

    # get prompts
    prompt_filepath = config.PROMPT_FILEPATH    
    messages = get_PA_prompt(prompt_filepath=prompt_filepath, commit_id=commit_id)

    # get response (do request)
    response_info, request_content = chatgpt_request.chatgpt_request(
        request_url=config.REQUEST_URL,
        api_key=config.OPENAI_API_KEY,
        model=config.REQUEST_MODEL,
        messages=messages
    )

    # save response
    # timestamp = response_parser.get_response_timestamp(response_info=response_info)
    response_filepath = get_path.get_response_filepath(task=task, commit_id=commit_id, timestamp=stamp)
    response_parser.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)

    # save parsed response
    parsed_response = parse_PA_response(response_info=response_info)
    parsed_response_path = get_path.get_parsed_response_filepath(task=task, commit_id=commit_id, timestamp=stamp)
    response_parser.save_parsed_response(response_dict=parsed_response, parsed_filepath=parsed_response_path)

    parsed_savepath = get_path.get_parsed_data_savepath(commit_id=commit_id, level='function', stamp=stamp)
    save_PA_parsed(parsed_response=parsed_response, parsed_savepath=parsed_savepath)

    return parsed_savepath