import os
import json

import config.config as config

import logging
logger = logging.getLogger(__name__)

def read_response_info(response_filepath):
    with open(response_filepath, 'r') as f:
        response_json = json.load(f)
    response_info = response_json['response']
    return response_info