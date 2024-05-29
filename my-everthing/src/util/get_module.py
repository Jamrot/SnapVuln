import os
import json
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from slicing import config

def get_criterion_meta(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)
    
def get_criterion_filepath(criterion):
    commit_id = criterion['commit_id']
    commit_id_short = commit_id[:8]
    func_name = criterion['func_name']
    criterion_line = criterion['criterion']['line']
    file_path_old = criterion['file_path']['old']
    return file_path_old

def get_module_path(meta_filepath):
    linux_root = config.LINUX    
    criterion = get_criterion_meta(meta_filepath)
    filepath = get_criterion_filepath(criterion[0])
    module_dir = os.path.dirname(filepath)
    module_path = os.path.join(linux_root, module_dir)
    print(os.path.exists(module_path))
    print(module_path)

if __name__=="__main__":
    criterion_meta_path = "my-everthing/data/test/0844370f/tls_strp_copyin-363/meta-0844370f-tls_strp_copyin-363.json"
    get_module_path(criterion_meta_path)
