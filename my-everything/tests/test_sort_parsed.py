import sys
import os
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src_new'))
sys.path.append(project_root)

from log_config.log_config import setup_logging

log_filename = os.path.join(os.path.dirname(__file__), 'log_test_sort_parsed.log')
setup_logging(log_filename=log_filename)
logger = logging.getLogger(__name__)

from api_requests.response_parser import do_sort_parsed

if __name__ == '__main__':
    parsed_savepath = "my-everything/data/test_slice/response/a282a2f/function.parsed/parsed-a282a2f-function-N20240624022117.json"
    do_sort_parsed(parsed_savepath)