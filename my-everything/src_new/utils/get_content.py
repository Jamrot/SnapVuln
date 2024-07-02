import os
import re
import json
import networkx as nx
from tqdm import tqdm

from analysis.patch_analyzer import PatchAnalyzer
from analysis.graph_builder import GraphBuilder
from analysis.criterion_extractor import CriterionExtractor
from slices.slicer_new import Slicer
import config.config as config
import utils.get_path as get_path
import api_requests.response_parser as response_parser
import slices.get_slice_results as get_slice_results

import logging
logger = logging.getLogger(__name__)

def get_all_criterions_from_root(root_dir):
    meta_filepath_list = get_path.get_all_meta_filepath_from_root(root_dir=root_dir)
    criterions = []
    for meta_filepath in meta_filepath_list:
        criterion = read_criterion_from_meta(meta_filepath=meta_filepath)
        if not criterion:
            logger.warning(f"Cannot get criterion from meta file: {meta_filepath}")
            continue
        criterions.append(criterion)
    
    return criterions


def read_criterion_from_meta(meta_filepath):
    with open(meta_filepath, 'r') as f:
        criterion = json.load(f)
    if not len(criterion)==1:
        logger.error(f"[Read criterion failed] Invalid criterion num from meta file: {meta_filepath}")
        return None
    criterion = criterion[0]
    return criterion