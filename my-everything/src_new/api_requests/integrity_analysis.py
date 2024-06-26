import json
import os
import logging
from tqdm import tqdm
import time

import config.config as config
import api_requests.chatgpt_request as chatgpt_request
import api_requests.response_parser as response_parser
import utils.get_path as get_path


def get_IA_prompt():
    # get patch information

    # get sliced code

    pass


def parse_IA_response(messages):
    pass


def do_IA_analysis(commit_id):
    task = "IA"

    # get prompts
    prompt_filepath = config.PROMPT_FILEPATH
    messages = get_IA_prompt(prompt_filepath=prompt_filepath, commit_id=commit_id)

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
    parsed_response = parse_IA_response(response_info=response_info)
    parsed_filepath = get_path.get_parsed_response_filepath(task=task, commit_id=commit_id, timestamp=timestamp)
    response_parser.save_parsed_response(response_dict=parsed_response, parsed_filepath=parsed_filepath)

    return parsed_filepath
    