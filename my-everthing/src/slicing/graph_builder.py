import os
import networkx as nx
from icecream import ic
import config
import logging

logger = logging.getLogger(__name__)

ic.configureOutput(includeContext=True)

class GraphBuilder:
    def __init__(self):
        # self.graph = graph
        pass

    def joern_parse(cls, source_path, bin_file = "tmp.bin"):
        cmd = f'joern-parse  {source_path} -o {bin_file} > /dev/null 2>&1'
        # ic(cmd)
        logger.info("[GraphBuilder] %s", cmd)
        os.system(cmd)

    def joern_dump_graph(self, graph_dir="out_tmp", bin_file="tmp.bin",  graph_type='cpg'):
        if os.path.exists(graph_dir):
            os.system(f'rm -rf {graph_dir}')
        cmd1 = f'joern-export --repr {graph_type} {bin_file} --out {graph_dir} > /dev/null 2>&1'
        # ic(cmd1)
        logger.info("[GraphBuilder] %s", cmd1)
        os.system(cmd1)
    
    def read_graph(self, graph_path):
        G = nx.drawing.nx_agraph.read_dot(graph_path)
        return G
    

    def combine_graph_in_dir(self, graph_dir):
        graph_filenames = os.listdir(graph_dir)
        G_combine = nx.DiGraph()
        for filename in graph_filenames:
            graph_filepath = os.path.join(graph_dir, filename)
            # G = nx.drawing.nx_agraph.read_dot(graph_filepath)
            G = self.read_graph(graph_filepath)
            G_combine.add_nodes_from(G.nodes(data=True))
            G_combine.add_edges_from(G.edges(data=True))
            # ic(G_combine.number_of_nodes(), G_combine.number_of_edges())
            logger.info(f"[GraphBuilder] Combine graph {filename} to G_combine")
        return G_combine
    
    def save_graph(self, save_path, G):
        nx.drawing.nx_agraph.write_dot(G, save_path)
        ic(save_path)


def test():
    src_file = "my-everthing/data/code/file_code_old-97bf6f81_145.c"
    graph_type = "all"
    graph_dir = f"tmp_{graph_type}"    
    graph_builder = GraphBuilder()
    graph_builder.joern_parse(src_file)
    graph_builder.joern_dump_graph(graph_dir=graph_dir, graph_type=graph_type)
    # G = graph_builder.read_graph("tmp_cpg14/0-cpg.dot")
    # pass
    # G_combine = graph_builder.combine_cpg14(graph_dir)
    # save_path = os.path.join(graph_dir, "_combine_.dot")
    # graph_builder.save_graph(save_path, G_combine)

if __name__=="__main__":
    test()