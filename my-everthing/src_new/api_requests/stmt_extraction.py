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


def get_SE_prompts_1(prompt_filepath, parsed_response, commit_info):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts['stmt_extraction']

    messages = prompt_template
    # parsed_response = json.loads(response_PA)

    stmt_info = []
    # commit_info: version, files [file_path, file_code, functions(func_name, func_line, func_code, func_stmt<added, deleted>)]
    for commit_id in commit_info:
        files = commit_info[commit_id]['files']
        for file in files:
            file_path = file['file_path']
            for function in file['functions']:
                func_name = function['func_name']
                func_stmt = function['func_stmt']
                added_stmt = func_stmt['added']
                deleted_stmt = func_stmt['deleted']
                for stmt in deleted_stmt:
                    line = stmt['line']
                    code = stmt['code']
                    stmt_info.append({
                        'file_path': file_path,
                        'function_name': func_name,
                        'line_changes': line,
                        'modification': 'DELETE',
                        'statement': code
                    })

                for stmt in added_stmt:
                    line = stmt['line']
                    code = stmt['code']
                    stmt_info.append({
                        'file_path': file_path,
                        'function_name': func_name,
                        'line_changes': line,
                        'modification': 'ADD',
                        'statement': code
                    })
    
    patch_info = parsed_response
    patch_info['patch_statements'] = stmt_info
        
    messages[-1]['content'] = messages[-1]['content'].format(patch_info)
    # print(messages[-1]['content'])
    return messages


def get_SE_prompts(prompt_filepath, parsed_response, commit_info):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts['stmt_extraction']

    messages = prompt_template
    # parsed_response = json.loads(response_PA)

    stmt_info = []
    # commit_info: version, files [file_path, file_code, functions(func_name, func_line, func_code, func_stmt<added, deleted>)]
    for commit_id in commit_info:
        files = commit_info[commit_id]['files']
        for file in files:
            file_path = file['file_path']
            for function in file['functions']:
                func_name = function['func_name']
                func_stmt = function['func_stmt']
                added_stmt = func_stmt['added']
                deleted_stmt = func_stmt['deleted']
                for stmt in deleted_stmt:
                    line = stmt['line']
                    code = stmt['code']
                    line_info = " | ".join([file_path['old'], file_path['new'], func_name, str(line)])
                    stmt_info.append({
                        'statement_info': line_info,
                        'modification': 'DELETE',
                        'statement': code
                    })

                # for stmt in added_stmt:
                #     line = stmt['line']
                #     code = stmt['code']
                #     line_info = " | ".join([file_path['old'], file_path['new'], func_name, str(line)])
                #     stmt_info.append({
                #         'statement_info': line_info,
                #         'modification': 'ADD',
                #         'statement': code
                #     })
    
    patch_info = parsed_response
    patch_info['patch_statements'] = stmt_info
        
    messages[-1]['content'] = messages[-1]['content'].format(patch_info)
    # print(messages[-1]['content'])
    return messages


def do_SE_request(messages):
    response_info, request_content = chatgpt_request.chatgpt_request(request_url=config.REQUEST_URL, api_key=config.OPENAI_API_KEY, model=config.REQUEST_MODEL, messages=messages)
    return response_info, request_content


def parse_SE_response(response_info):
    response_content = chatgpt_request.get_response_content(response_info)
    response_dict = json.loads(response_content)
    # TODO: check if the response is in the correct format
    return response_dict


def save_SE_response(response_info, request_content, commit_id):
    response_dir = os.path.join(config.RESPONSE_DIR, 'SE')
    response_filename = get_path.get_response_filename(response_type='SE', commit_id=commit_id, parsed=False)
    response_filepath = os.path.join(response_dir, response_filename)
    chatgpt_request.save_response(response=response_info, response_filepath=response_filepath, request_content=request_content)


def save_SE_parse(response_dict, commit_id):
    parsed_dir = os.path.join(config.PARSED_DIR, 'SE')
    if not os.path.exists(parsed_dir):
        os.makedirs(parsed_dir)
    parsed_filename = get_path.get_response_filename(response_type='SE', commit_id=commit_id, parsed=True)
    parsed_filepath = os.path.join(parsed_dir, parsed_filename)
    with open(parsed_filepath, 'w') as f:
        json.dump(response_dict, f, indent=2)
    

def read_parsed_response(filepath):
    with open(filepath, 'r') as f:
        parsed_response = json.load(f)
    return parsed_response


def test():
    commit_id = config.COMMIT_ID
    filepath = "my-everthing/responses/parsed/PA/parsed_PA-a282a2f-20240617053613.json"
    parsed_response = read_parsed_response(filepath)

    prompt_filepath = config.PROMPT_FILEPATH    
    patch_desc, patch_diff_code, patch_info = chatgpt_request.get_patch(commit_id)
    messages = get_SE_prompts(prompt_filepath=prompt_filepath, parsed_response=parsed_response, commit_info=patch_info)

    response_info, request_content = do_SE_request(messages)

    save_SE_response(response_info=response_info, request_content=request_content, commit_id=commit_id)

    # filepath = "my-everthing/responses/original/SE/response_SE-a282a2f-20240617062716.json"
    # response_info = read_file.read_response_info(response_filepath=filepath)
    response_SE = parse_SE_response(response_info)
    save_SE_parse(response_dict=response_SE, commit_id=commit_id)
