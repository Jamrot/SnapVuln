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


def get_SE_prompts(prompt_filepath, parsed_response, commit_id):
    
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)    
    prompt_template = all_prompts[config.PROMPT_STMT_EXTRACTION]

    desc_clean, diff_code, commit_info = response_parser.get_patch(commit_id)

    messages = prompt_template
    # parsed_response = json.loads(response_PA)

    prompt_stmt = []
    # commit_info: version, files [file_path, file_code, functions(func_name, func_line, func_code, func_stmt<added, deleted>)]
    for commit_id in commit_info:
        files = commit_info[commit_id]['files']
        for file_info in files:
            file_path = file_info['file_path']
            for func_info in file_info['functions']:
                func_name = func_info['func_name']
                func_stmt = func_info['func_stmt']
                add_stmt = func_stmt['added']
                del_stmt = func_stmt['deleted']
                for stmt_info in del_stmt:
                    modification = 'DELETE'
                    line_info, code = response_parser.get_line_info(file_path, func_name, stmt_info, modification)
                    prompt_stmt.append({
                        'statement_info': line_info,
                        'modification': modification,
                        'statement': code
                    })

                # for stmt_info in add_stmt:
                #     modification = 'ADD'
                #     line_info, code = response_parser.get_line_info(file_path, func_name, stmt_info, modification)
                #     stmt_info.append({
                #         'statement_info': line_info,
                #         'modification': modification,
                #         'statement': code
                #     })
    
    patch_info = parsed_response
    patch_info['patch_statements'] = prompt_stmt
        
    messages[-1]['content'] = messages[-1]['content'].format(patch_info)
    
    return messages


def do_SE_request(messages):
    response_info, request_content = chatgpt_request.chatgpt_request(request_url=config.REQUEST_URL, api_key=config.OPENAI_API_KEY, model=config.REQUEST_MODEL, messages=messages)
    return response_info, request_content


def parse_SE_response(response_info):
    response_content = response_parser.get_response_content(response_info)
    response_dict = json.loads(response_content)
    # TODO: check if the response is in the correct format
    return response_dict


def save_SE_parsed(parsed_response, commit_id, stamp):
    parsed_savepath = get_path.get_parsed_savepath_from_criterion(commit_id=commit_id, level='function', stamp=stamp)

    stmt_info = parsed_response.get("statement_info", "")
    modification = parsed_response.get("modification", "")
    statement = parsed_response.get("statement", "")
    reason = parsed_response.get("reason", "")

    parsed_data = response_parser.read_parsed(parsed_savepath=parsed_savepath)
    parsed_data["SE_statement_info"] = stmt_info
    parsed_data["SE_modification"] = modification
    parsed_data["SE_statement"] = statement
    parsed_data["SE_reason"] = reason

    response_parser.save_parsed(parsed_data=parsed_data, parsed_savepath=parsed_savepath)

    return parsed_savepath


def do_stmt_extraction(commit_id, filepath_PA):
    task = "SE"

    # get prompts
    prompt_filepath = config.PROMPT_FILEPATH
    parsed_response = response_parser.read_parsed_response(filepath_PA)
    messages = get_SE_prompts(prompt_filepath=prompt_filepath, parsed_response=parsed_response, commit_id=commit_id)

    # get response
    response_info, request_content = do_SE_request(messages)

    # save response
    timestamp = response_parser.get_response_timestamp(response_info)
    response_filepath = get_path.get_response_filepath(task=task, commit_id=commit_id, timestamp=timestamp)
    response_parser.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)

    # save parsed response
    parsed_response = parse_SE_response(response_info=response_info)
    parsed_filepath = get_path.get_parsed_filepath(task=task, commit_id=commit_id, timestamp=timestamp)
    response_parser.save_parsed_response(response_dict=parsed_response, parsed_filepath=parsed_filepath)

    return parsed_filepath
