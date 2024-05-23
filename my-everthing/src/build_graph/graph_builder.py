import os
import networkx as nx
from icecream import ic

class GraphBuilder:
    def __init__(self, graph):
        self.graph = graph

    @classmethod
    def joern_parse(cls, source_file, bin_file):
        cmd = f'joern-parse  {source_file} -o {bin_file} > /dev/null 2>&1'
        ic(cmd)
        os.system(cmd)

    def joern_dump_graph(self, bin_file, graph_dir, graph_type='cfg'):
        if os.path.exists(graph_dir):
            os.system(f'rm -rf {graph_dir}')
        cmd1 = f'joern-export --repr {graph_type} {bin_file} --out {graph_dir} > /dev/null 2>&1'
        ic(cmd1)
        os.system(cmd1)
    
    def read_graph(self, graph_path):
        G = nx.drawing.nx_agraph.read_dot(graph_path)
        # save
        # nx.drawing.nx_agraph.write_dot(G, graph_path)
        # ic(graph_path)