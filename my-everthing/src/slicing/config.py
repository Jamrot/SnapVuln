import os
LINUX = '/mnt/wsl2/home/jamrot/linux'

DATA_ROOT = '/app/slicing-snapvuln/my-everthing/data'
# GRAPH_ROOT = os.path.join(DATA_ROOT, 'graph')
# CODE_ROOT = os.path.join(DATA_ROOT, 'code')
GRAPH_ROOT = os.path.join(DATA_ROOT, 'test')
CODE_ROOT = os.path.join(DATA_ROOT, 'test')
SLICE_ROOT = os.path.join(DATA_ROOT, 'test')

desc_tags_prefixes = [
    "Signed-off-by:", "Reported-by:", "Fixes:", "Link:", "Suggested-by:", "cc:",
    "Tested-by:", "Acked-by:", "Reviewed-by:", "CC:", "Fixes:", "Cc:", "Requested-by:", 
    "Reported by:", "(Merged from", "Reported-and-tested-by:", "Closes:", "Message-Id:", 
    "Reviewed by:", "Sponsored by:", "Differential revision:", "Submitted by"
]
