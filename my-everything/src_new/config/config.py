import os
LINUX = '/mnt/wsl2/home/jamrot/linux'

DATA_ROOT = '/app/slicing-snapvuln/my-everything/data/test_slice/20240704'

CODE_ROOT_DIRNAME = 'code'
OLD_CODE_DIRNAME = 'code_old'
NEW_CODE_DIRNAME = 'code_new'
GRAPH_ROOT_DIRNAME = 'graph'
SLICE_ROOT_DIRNAME = 'slice'
META_ROOT_DIRNAME = "meta"

desc_tags_prefixes = [
    "Signed-off-by:", "Reported-by:", "Fixes:", "Link:", "Suggested-by:", "cc:",
    "Tested-by:", "Acked-by:", "Reviewed-by:", "CC:", "Fixes:", "Cc:", "Requested-by:", 
    "Reported by:", "(Merged from", "Reported-and-tested-by:", "Closes:", "Message-Id:", 
    "Reviewed by:", "Sponsored by:", "Differential revision:", "Submitted by"
]

GRAPH_START = 'graph'
GRAPH_DIR_END = '.graph'
GRAPH_FILE_END = '.dot'

SLICE_START = 'slice'
SLICE_DIR_END = '.slice'
SLICE_DOT_FILE_END = '.slice_code.dot'
SLICE_CODE_FILE_END = '.slice_code.md'
SLICE_CODE_FILE_END_JSON = '.slice_code.json'
SLICE_INFO_FILE_END = '.slice_info.json'

PARSED_START = 'parsed'
PARSED_DIR_END = '.parsed'
PARSED_FILE_END = '.json'

META_START = 'meta'
META_FILE_END = '.json'

CODE_FILENAME_START = 'file_code_old'
MODULE_DIRNAME_START = 'module'

CODE_FILE_OVERWRITE = False
MODULE_OVERWRITE = False
BIN_OVERWRITE = False
GRAPH_OVERWRITE = False
GRAPH_ALL_OVERWRITE = False

# patch
COMMIT_ID = "a282a2f10539dce2aa619e71e1817570d557fc97"
# COMMIT_ID = "6825bdde44340c5a9121f6d6fa25cc885bd9e821"

# prompt
PROMPT_FILEPATH = "my-everything/prompts/prompt-dump.json"
PROMPT_STMT_EXTRACTION = "stmt_extraction"
PROMPT_PATCH_ANALYSIS = "patch_analysis"
PROMPT_SLICING_STRATEGY = "slicing_strategy_stmt"
PROMPT_CORE_OPERATIONS = "core_operations"
PROMPT_INTEGRITY_ANALYSIS = "integrity_analysis"
PROMPT_FURTHER_SLICING = "further_slicing"

# requests
REQUEST_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REQUEST_MODEL = "gpt-4-0613"

RESPONSE_DIR = '/app/slicing-snapvuln/my-everything/responses/original'
PARSED_DIR = '/app/slicing-snapvuln/my-everything/data/test_api/parsed_response'

PA_RESPONSE_FILEPATH = "my-everything/responses/parsed/PA/parsed_PA-a282a2f-20240617053613.json"
SE_RESPONSE_FILEPATH = "my-everything/responses/parsed/SE/parsed_SE-a282a2f-20240617073944.json"

# slicing
# PARSED_FILEPATH = "my-everything/data/test_slice/response/a282a2f-2/parsed/function.parsed/gpt-4-0613/sorted_parsed-a282a2f-function-gpt-4-0613-N20240624092357.json"
PARSED_FILEPATH = "my-everything/data/test_slice/response/a282a2f/parsed/function.parsed/gpt-4-0613/parsed-a282a2f-function-gpt-4-0613-N20240624092357.json"


# time
from datetime import datetime
CURRENT_TIME = datetime.now().strftime("N%Y%m%d%H%M%S")