import config.config as config
import os
import json
import datetime

import logging
logger = logging.getLogger(__name__)

from analysis.patch_analyzer import PatchAnalyzer
import utils.get_path as get_path


def read_parsed_response(response_filepath):
    with open(response_filepath, 'r') as f:
        response = json.load(f)
    return response


def read_single_response(response_filepath):
    with open(response_filepath, 'r') as f:
        response_json = json.load(f)
    
    response = response_json['response']['choices'][0]['message']['content']
    return response


def read_response_info(response_filepath):
    with open(response_filepath, 'r') as f:
        response_json = json.load(f)
    response_info = response_json['response']
    return response_info


def get_response_content(response_info):
    response_content = response_info['choices'][0]['message']['content']
    response_content = response_content.replace('```json', '').strip("```")
    return response_content


def get_response_timestamp(response_info):
    timestamp = response_info.get("created")
    if not timestamp:
        timestamp = 'N'+datetime.datetime.now().timestamp()
    dt = datetime.datetime.fromtimestamp(timestamp)
    timestamp_str = dt.strftime('%Y%m%d%H%M%S')
    return timestamp_str


def save_response(response, response_filepath, request_content=""):
    save_content = {
        "request": request_content,
        "response": response        
    }
    save_dir = os.path.dirname(response_filepath)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(response_filepath, 'w') as f:
        json.dump(save_content, f, indent=2)


def save_strategy():
    # TODO: save slicing strategy for each criterion
    pass


def get_patch(commit_id):
    patch_analyzer = PatchAnalyzer(url=config.LINUX, commit_id=commit_id)
    _, clean_desc = patch_analyzer.get_description()
    diff_code = patch_analyzer.get_diff_code()
    info = patch_analyzer.get_commit_info()
    return clean_desc, diff_code, info