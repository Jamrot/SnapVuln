import os
import config
from graph_builder import GraphBuilder
import logging
from icecream import ic

logger = logging.getLogger(__name__)

def build_graph_from_file_code_old():
    graph_builder = GraphBuilder()
    code_dir = config.CODE_ROOT
   
    code_filenames = os.listdir(code_dir)
    for filename in code_filenames:        
        graph_dir = os.path.join(config.GRAPH_ROOT, filename)
        if not os.path.exists(graph_dir):
            os.makedirs(graph_dir) 

        file_path = os.path.join(code_dir, filename)
        
        bin_file = os.path.join(graph_dir, f"{filename}.bin")
        graph_builder.joern_parse(file_path, bin_file)

        graph_dump_dir = os.path.join(graph_dir, "dump")
        graph_builder.joern_dump_graph(bin_file, graph_dump_dir)

        graph_path = os.path.join(graph_dump_dir, filename, "_global_.dot")
        G = graph_builder.read_graph(graph_path)

def build_graph_from_file_code(graph_type="all"):
    graph_builder = GraphBuilder()
    code_dir = config.CODE_ROOT

    code_commit_ids = os.listdir(code_dir)
    for commit_id in code_commit_ids:
        commit_id_dir = os.path.join(code_dir, commit_id)
        code_filenames = os.listdir(commit_id_dir)
        for filename in code_filenames:
            if not filename.endswith(".c"):
                continue  
            graph_dir = os.path.join(config.GRAPH_ROOT, commit_id, filename.replace(".c", ".graph"))
            if not os.path.exists(graph_dir):
                os.makedirs(graph_dir) 

            code_filepath = os.path.join(code_dir, commit_id, filename)
            
            bin_file = os.path.join(graph_dir, f"{filename}.bin")
            graph_builder.joern_parse(code_filepath, bin_file)

            # graph_type = "all"
            graph_dump_dir = os.path.join(graph_dir, "graph_"+graph_type)
            graph_builder.joern_dump_graph(graph_dir=graph_dump_dir, bin_file=bin_file, graph_type=graph_type)

            graph_path = get_graph_filepath_from_dump_dir(graph_dump_dir, graph_type)

            save_path = os.path.join(graph_dir, f"graph_{graph_type}-{filename}.dot")
            # copy the graph file to the graph_dir
            if not graph_path:
                try:
                    G_combine = graph_builder.combine_graph_in_dir(graph_dump_dir)
                    graph_builder.save_graph(save_path, G_combine)
                except Exception as e:
                    ic(e)
            os.system(f"cp {graph_path} {save_path}")
            ic(save_path)


def get_graph_filepath_from_dump_dir(graph_dump_dir, graph_type):
    graph_filepath = ""
    if graph_type == "all":
        graph_filepath = os.path.join(graph_dump_dir, "export.dot")
    elif graph_type == "cpg":
        graph_filepath = os.path.join(graph_dump_dir, "_global_.dot")
    else:
        ic(f"Invalid graph type: {graph_type}")
        # raise ValueError(f"Invalid graph type: {graph_type}")

    ic(graph_filepath)
    return graph_filepath

if __name__ == '__main__':
    build_graph_from_file_code()