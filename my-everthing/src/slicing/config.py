import os
LINUX = '/mnt/wsl2/home/jamrot/linux'

DATA_ROOT = '/app/slicing-snapvuln/my-everthing/data'
# GRAPH_ROOT = os.path.join(DATA_ROOT, 'graph')
# CODE_ROOT = os.path.join(DATA_ROOT, 'code')
GRAPH_ROOT = os.path.join(DATA_ROOT, 'test')
CODE_ROOT = os.path.join(DATA_ROOT, 'test')
SLICE_ROOT = os.path.join(DATA_ROOT, 'test')
META_ROOT = os.path.join(DATA_ROOT, 'test')

desc_tags_prefixes = [
    "Signed-off-by:", "Reported-by:", "Fixes:", "Link:", "Suggested-by:", "cc:",
    "Tested-by:", "Acked-by:", "Reviewed-by:", "CC:", "Fixes:", "Cc:", "Requested-by:", 
    "Reported by:", "(Merged from", "Reported-and-tested-by:", "Closes:", "Message-Id:", 
    "Reviewed by:", "Sponsored by:", "Differential revision:", "Submitted by"
]

CODE_FILENAME_START = 'file_code_old'
META_FILENAME_START = 'meta'
MODULE_DIRNAME_START = 'module'

GRAPH_START = 'graph'

GRAPH_DIR_END = '.graph'
GRAPH_FILE_END = '.dot'

MODULE_OVERWRITE = True
BIN_OVERWRITE = False
GRAPH_OVERWRITE = False

BIN_CONFIRM = False
MODULE_CONFIRM = False
CODE_FILE_CONFIRM = False