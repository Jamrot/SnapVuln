import sys
import os
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src_new'))
sys.path.append(project_root)

from log_config.log_config import setup_logging

log_filename = os.path.join(os.path.dirname(__file__), 'log_test_slice_further.log')
setup_logging(log_filename=log_filename)
logger = logging.getLogger(__name__)

import slices.slice_further as slice_further

if __name__ == '__main__':
    slice_further.test()