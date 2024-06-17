import sys
import os
import logging.config
import yaml


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(os.path.join(project_root, 'src_new'))


from log_config.log_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
