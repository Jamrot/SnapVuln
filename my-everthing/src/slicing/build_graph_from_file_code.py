import os
import config
from graph_builder import GraphBuilder

def build_graph_from_file_code():
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

if __name__ == '__main__':
    build_graph_from_file_code()