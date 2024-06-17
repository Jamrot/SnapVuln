import json
from analysis.patch_analyzer import PatchAnalyzer
import config.config as config

"""get prompts"""
def get_patch(commit_id):
    patch_analyzer = PatchAnalyzer(url=config.LINUX, commit_id=commit_id)
    _, desc = patch_analyzer.get_description()
    code = patch_analyzer.get_diff_code()
    commit_info = patch_analyzer.get_commit_info()
    return desc, code, commit_info


def get_PA_prompts(prompt_filepath, patch):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts['patch_analysis']

    messages = prompt_template
    messages[-1]['content'] = messages[-1]['content'].format(patch)

    return messages


def get_SE_prompts(prompt_filepath, response_PA, commit_info):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts['stmt_extraction']

    messages = prompt_template
    parsed_response = json.loads(response_PA)

    stmt_info = []
    """
    dict: Commit information with the following keys:
            - version: {'old': str, 'new': str}
            - files: [{
                - 'file_path': {'old': str, 'new': str}, 
                - 'file_code': {'old': str, 'new': str}, 
                - 'functions': [{
                    - 'func_name': str, 
                    - 'func_line': {'start': int, 'end': int}, 
                    - 'func_code': {'old': str, 'new': str}, 
                    - 'func_stmt': {'added': [{'line': int, 'code': str}], 'deleted': [{'line': int, 'code': str}]}}]}]
    """
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

                # for stmt in added_stmt:
                #     line = stmt['line']
                #     code = stmt['code']
                #     stmt_info.append({
                #         'file_path': file_path,
                #         'function_name': func_name,
                #         'line_changes': line,
                #         'modification': 'ADD',
                #         'statement': code
                #     })
    
    patch_info = parsed_response
    patch_info['patch_statements'] = stmt_info
        
    messages[-1]['content'] = messages[-1]['content'].format(patch_info)
    # print(messages[-1]['content'])
    return messages


def get_SS_prompts(prompt_filepath, response_PA, commit_diff_code):
    with open(prompt_filepath, 'r') as f:
        all_prompts = json.load(f)
    
    prompt_template = all_prompts['slicing_strategy']

    messages = prompt_template
    parsed_response = json.loads(response_PA)

    patch_info = parsed_response
    patch_info['related_code'] = commit_diff_code

    messages[-1]['content'] = messages[-1]['content'].format(patch_info)

    return messages