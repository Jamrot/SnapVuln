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
from slices.slice_from_response import *

import logging
logger = logging.getLogger(__name__)


def test():
    commit_id = config.COMMIT_ID

    parsed_filepath = "my-everything/data/test_slice/response/a282a2f/parsed/function.parsed/gpt-4-0613/parsed-a282a2f-function-gpt-4-0613-N20240624092357.json"
    parsed_response = response_parser.read_parsed(parsed_filepath)

#     parsed_response = {"further_slicing": [{
#       "statement_info": "code/code_old/net/ceph/messenger_v2.c | static int decode_preamble(void *p, struct ceph_frame_desc *desc) | L519",
#       "statement": "desc->fd_lens[i] = ceph_decode_32(&p);",
#       "slicing_direction": "forward",
#       "code_representation_graph": "Data Dependency Graph",
#       "justification": "This statement is responsible for decoding the segment lengths, which are later checked for validity. A forward slice from this statement will include all statements that are affected by the decoded lengths, which is crucial for understanding the vulnerability."
#     }
#   ]
# }
    criterion_extractor = CriterionExtractor(url=config.LINUX, commit_id=commit_id)
    matched_criterions = criterion_extractor.get_criterion_from_response(parsed_response=parsed_response)

    # build dump graph
    graph_dump_type = "all"
    graph_level = "file" # function, file, module
    build_level_graph(graph_dump_type=graph_dump_type, criterions=matched_criterions, level=graph_level)
    
    G_filename_dict = {} # dict for all nodes and edges graph
    for criterion in matched_criterions:
        graph_save_path = get_path.get_graph_savepath_from_criterion(criterion=criterion, graph_type="all_filename", graph_level=graph_level)
        if graph_save_path not in G_filename_dict:
            G_filename = add_filename_from_parent(criterion=criterion, graph_level=graph_level, graph_type=graph_dump_type)
            G_filename_dict[graph_save_path] = G_filename
    
    G_filename = None
    collate_info_dict = {'code':{}, 'nodes':{}, 'edges':{}}
    collate_codes = []
    for criterion in matched_criterions:
        # graph_type = "all"
        graph_save_path = get_path.get_graph_savepath_from_criterion(criterion=criterion, graph_type="all_filename", graph_level=graph_level)
        slice_direction = criterion['direction']
        slice_graph = criterion['graph']
        slice_depth = graph_level
        G_filename = G_filename_dict[graph_save_path]
        logger.info("graph_save_path: %s", graph_save_path)
        slice_save_path, G_slice = build_single_slice(
            criterion=criterion,
            slice_direction=slice_direction,
            slice_graph=slice_graph,
            slice_depth=slice_depth,
            graph_type=graph_dump_type,
            G_grpah=G_filename)
        
        slice_save_path = get_path.get_slice_savepath_from_criterion(criterion=criterion, direction=slice_direction, graph_type=slice_graph, depth=slice_depth)

        slice_info_dict = get_slice_results.get_slice_info_from_dot_criterion(criterion=criterion, myslice_filepath=slice_save_path, level=slice_depth, G_slice=None)
        get_slice_results.get_slice_codes_json_from_info(slice_info_dict=slice_info_dict, myslice_filepath=slice_save_path, commit_id=commit_id)
        get_slice_results.get_slice_codes_from_info(slice_info_dict=slice_info_dict, myslice_filepath=slice_save_path, commit_id=commit_id)

        collate_info_dict = get_slice_results.collate_slice_info(slice_info_dict=slice_info_dict, collate_info_dict=collate_info_dict)
    
    collate_savepath = get_path.get_collate_slice_savepath(commit_id=commit_id, slice_depth=slice_depth)
    get_slice_results.get_slice_codes_json_from_info(slice_info_dict=collate_info_dict, myslice_filepath=collate_savepath, commit_id=commit_id)
    get_slice_results.get_slice_codes_from_info(slice_info_dict=collate_info_dict, myslice_filepath=collate_savepath, commit_id=commit_id)
    get_slice_results.save_collate_slice_info(collate_info_dict=collate_info_dict, collate_save_filepath=collate_savepath)

    pass