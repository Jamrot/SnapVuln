import config.config as config
import os
import json
import logging
from analysis.patch_analyzer import PatchAnalyzer

logger = logging.getLogger(__name__)


def read_response(response_filepath):
    with open(response_filepath, 'r') as f:
        response = json.load(f)
    return response

def parse_PA_response(response):
    # {\n  \"patch_summary\": \"The patch adds checks to ensure segment lengths in the Ceph messenger protocol are within valid ranges to prevent buffer overruns.\",\n  \"vulnerability_type\": \"Buffer Overflow\",\n  \"vulnerability_summary\": \"The vulnerability allows a buffer overrun due to improper handling of segment lengths, which can be manipulated to cause negative values leading to insufficient buffer allocation.\"\n}"

    response_dict = json.loads(response)
    patch_summary = response_dict["patch_summary"]
    vulnerability_type = response_dict["vulnerability_type"]
    vulnerability_summary = response_dict["vulnerability_summary"]

# def get_SE_prompt(response):
#     patch_analyzer = PatchAnalyzer()
#     get_modification_stmts()
#     response_dict = json.loads(response)

def save_strategy():
    # TODO: save slicing strategy for each criterion
    pass

def get_patch(commit_id):
    patch_analyzer = PatchAnalyzer(url=config.LINUX, commit_id=commit_id)
    _, desc = patch_analyzer.get_description()
    code = patch_analyzer.get_commit_info()
    print(code['files'][0])
    return desc, code

def test():
    commit_id = "a282a2f10539dce2aa619e71e1817570d557fc97"
    desc, code = get_patch(commit_id)


if __name__ == "__main__":
    test()