import config
import os
import json
import logging

logger = logging.getLogger(__name__)

class ResponseParser:
    def __init__(self):
        pass

    def read_response(self, response_filepath):
        with open(response_filepath, 'r') as f:
            response = json.load(f)
        return response
    
    def parse_response(self, response):
        pass