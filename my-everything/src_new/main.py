import sys
import os
import logging.config
import yaml


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(os.path.join(project_root, 'src_new'))

from log_config.log_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


from config import config
from utils.get_time import get_time

from analysis.criterion_extractor import CriterionExtractor
from api_requests.patch_analysis import do_patch_analysis
from api_requests.stmt_extraction import do_stmt_extraction
from api_requests.slicing_strategy import do_slicing_strategy
from api_requests.core_operations import do_core_operations
from api_requests.integrity_analysis import do_integrity_analysis
from api_requests.further_slicing import do_further_slicing
from slices.slice_from_strategy import slice_from_strategy

def main():
    commit_id = config.COMMIT_ID
    # stamp = get_time()
    stamp = '20240708083706'
    # request patch analysis
    # parsed_savepath = do_patch_analysis(commit_id, stamp)
    # # request statements extraction
    # parsed_savepath = do_stmt_extraction(commit_id, stamp)
    # # # request slicing strategy (function)
    # parsed_savepath = do_slicing_strategy(commit_id, stamp)
    # # slice (function)
    slice_depth = 'function'
    # slice_from_strategy(slice_depth="function", match_criterion="patch", url=config.LINUX, commit_id=commit_id, parsed_filepath=parsed_savepath)
    # # request core operations
    # parsed_savepath = do_core_operations(commit_id, stamp, slice_depth)
    # # request integrity analysis
    # parsed_savepath = do_integrity_analysis(commit_id, stamp, slice_depth)
    # request further slicing strategy (file)
    parsed_savepath = do_further_slicing(commit_id, stamp, slice_depth)
    # slice (file)
    slice_from_strategy(slice_depth="file", match_criterion="response", url=config.LINUX, commit_id=commit_id, parsed_filepath=parsed_savepath)

if __name__=="__main__":
    main()