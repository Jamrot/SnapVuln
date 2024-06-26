import sys
import os
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src_new'))
sys.path.append(project_root)

from log_config.log_config import setup_logging

log_filename = os.path.join(os.path.dirname(__file__), 'log_test_chatgpt_request.log')
setup_logging(log_filename=log_filename)
logger = logging.getLogger(__name__)

import api_requests.stmt_extraction as stmt_extraction
import api_requests.patch_analysis as patch_analysis
import api_requests.slicing_strategy as slicing_strategy
import config.config as config
from api_requests.response_parser import do_sort_parsed

if __name__ == '__main__':
    commit_id = config.COMMIT_ID
    # stamp = config.CURRENT_TIME
    stamp = "N20240624092357"
    # patch_analysis.do_patch_analysis(commit_id, stamp)
    # stmt_extraction.do_stmt_extraction(commit_id, stamp)
    parsed_savepath = slicing_strategy.do_slicing_strategy(commit_id, stamp)
    # patch_analysis.test()
    # stmt_extraction.test()
    # slicing_strategy.test()
    # do_sort_parsed(parsed_savepath)