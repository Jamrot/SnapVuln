import os
LINUX = '/mnt/wsl2/home/jamrot/linux'

DATA_ROOT = '/app/slicing-snapvuln/my-everthing/data/test'
# GRAPH_ROOT = os.path.join(DATA_ROOT, 'graph')
# CODE_ROOT = os.path.join(DATA_ROOT, 'code')
# GRAPH_ROOT = os.path.join(DATA_ROOT, 'test')
# CODE_ROOT = os.path.join(DATA_ROOT, 'test')
# SLICE_ROOT = os.path.join(DATA_ROOT, 'test')
# META_ROOT = os.path.join(DATA_ROOT, 'test')

GRAPH_ROOT = CODE_ROOT = SLICE_ROOT = META_ROOT = DATA_ROOT

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

SLICEs_START = 'graph'
SLICE_DIR_END = '.slice'
SLICE_DOT_FILE_END = '.slice_code.dot'

CODE_FILE_OVERWRITE = False
MODULE_OVERWRITE = False
BIN_OVERWRITE = False
GRAPH_OVERWRITE = False
GRAPH_ALL_OVERWRITE = False

BIN_CONFIRM = False
MODULE_CONFIRM = False
CODE_FILE_CONFIRM = False


# patch
COMMIT_ID = "a282a2f10539dce2aa619e71e1817570d557fc97"
# COMMIT_ID = "6825bdde44340c5a9121f6d6fa25cc885bd9e821"
PROMPT_FILEPATH = "my-everthing/prompts/prompt.json"

# requests
REQUEST_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REQUEST_MODEL = "gpt-4o"

RESPONSE_DIR = '/app/slicing-snapvuln/my-everthing/responses/original'
PARSED_DIR = '/app/slicing-snapvuln/my-everthing/responses/parsed'