import sys
import json
import os
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src_new'))
sys.path.append(project_root)

from log_config.log_config import setup_logging

log_filename = os.path.join(os.path.dirname(__file__), 'log_test_file_slice.log')
setup_logging(log_filename=log_filename)
logger = logging.getLogger(__name__)

from slices.slicer_new import Slicer
from analysis.graph_builder import GraphBuilder


def add_filename_from_parent(graph_dump_filepath, graph_filename_savepath):
    # read graph from graph_dump_filepath
    graph_builder = GraphBuilder()    
    G = graph_builder.read_graph(graph_dump_filepath)

    for node in G.nodes(data=True):
        node_id = node[0]
        node_data = node[1]
        
        # check if the node is a FILE or has FILENAME attribute
        node_label = node_data.get('label')
        node_filename = node_data.get('FILENAME')
        node_name = node_data.get('NAME')

        if node_label == "FILE" and node_name:
            G.nodes[node_id]['filename'] = node_name
        elif node_filename:
            G.nodes[node_id]['filename'] = node_filename
        else:
            for parent in G.predecessors(node_id):
                parent_data = G.nodes[parent]
                parent_label = parent_data.get('label')
                parent_filename = parent_data.get('FILENAME')
                parent_name = parent_data.get('NAME')

                if parent_label == "FILE" and parent_name:
                    G.nodes[node_id]['filename'] = parent_name
                    break
                elif parent_filename:
                    G.nodes[node_id]['filename'] = parent_filename
                    break
    
    # save graph to graph_filename_savepath
    graph_builder.save_graph(G=G, save_path=graph_filename_savepath)
    return G


def get_code_from_dot(G, code_root="/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/code/test"):
    codes = {}
    for node in G.nodes(data=True):
        filename = node[1].get('filename')
        location = node[1].get('LINE_NUMBER')
        if filename and location:
            code_path = os.path.join(code_root, filename)
            with open(code_path, 'r') as f:
                lines = f.readlines()
                code = lines[int(location)-1]
            if filename not in codes:
                codes[filename] = {}
            codes[filename][location] = code
        else:
            print(f"Node {node[1]} does not have filename or location")
    
    sorted_codes = {}
    for filename, code_dict in codes.items():
        sorted_codes[filename] = dict(sorted(code_dict.items(), key=lambda x: int(x[0])))

    return sorted_codes


import os
import re
import shutil

def parse_includes(file_path):
    """
    解析源文件中的包含指令并返回头文件列表。
    """
    includes = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'#include\s+[<"](.*?)[>"]', line)
            if match:
                includes.append(match.group(1))
    return includes

def find_include_paths(include_list, search_dirs):
    """
    查找头文件的路径，返回字典{头文件: 文件路径}。
    """
    include_paths = {}
    for include in include_list:
        for dir in search_dirs:
            include_path = os.path.join(dir, include)
            if os.path.exists(include_path):
                include_paths[include] = include_path
                break
    return include_paths

def copy_includes(include_paths, dest_dir):
    """
    复制头文件到目标文件夹中。
    """
    for include, path in include_paths.items():
        dest_path = os.path.join(dest_dir, include)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copyfile(path, dest_path)
        print(f"Copied {path} to {dest_path}")


def test_include():
    source_file = '/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/code/test/code_new/messenger_v2.c'
    dest_dir = '/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/code/test/include'
    search_dirs = [
        '/mnt/wsl2/home/jamrot/linux/include'
    ]

    include_list = parse_includes(source_file)
    include_paths = find_include_paths(include_list, search_dirs)
    copy_includes(include_paths, dest_dir)


def test_slice():
    graph_builder = GraphBuilder()
    joern_parse_path = "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/code/test"
    bin_filepath = "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/graph/test/test.bin"
    graph_builder.joern_parse(source_path=joern_parse_path, bin_file=bin_filepath)

    graph_dump_dir = "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/graph/test/test-graph_dump"
    graph_builder.joern_dump_graph(graph_dir=graph_dump_dir, bin_file=bin_filepath, graph_type="all")

    
    graph_dump_path = os.path.join(graph_dump_dir, "export.dot")
    graph_save_path = "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/graph/test/test-graph-filename.dot"
    G_filename = add_filename_from_parent(graph_dump_filepath=graph_dump_path, graph_filename_savepath=graph_save_path)

    slicer = Slicer(G_graph=G_filename)
    G_slice = slicer.build_slice(criterion_linenum=519, direction='forward', slice_graph='ddg', depth='file')

    slice_save_path = "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/graph/test/test-graph-slice.dot"
    slicer.save_graph(G=G_slice, save_path=slice_save_path) 
    # G_slice = graph_builder.read_graph(slice_save_path)
    
    codes = get_code_from_dot(G=G_slice, code_root=joern_parse_path)
    with open("/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/graph/test/test-graph-slice-forward-code.json", 'w') as f:
        json.dump(codes, f, indent=2)

if __name__ == '__main__':
    # test_include()
    test_slice()
    