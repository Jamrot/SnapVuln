import os
import networkx as nx
from icecream import ic
import config

ic.configureOutput(includeContext=True)

class GraphBuilder:
    def __init__(self):
        # self.graph = graph
        pass

    @classmethod
    def joern_parse(cls, source_file, bin_file = "tmp.bin"):
        cmd = f'joern-parse  {source_file} -o {bin_file} > /dev/null 2>&1'
        ic(cmd)
        os.system(cmd)

    @classmethod
    def joern_dump_graph(self, graph_dir="out_tmp", bin_file="tmp.bin",  graph_type='cpg'):
        if os.path.exists(graph_dir):
            os.system(f'rm -rf {graph_dir}')
        cmd1 = f'joern-export --repr {graph_type} {bin_file} --out {graph_dir} > /dev/null 2>&1'
        ic(cmd1)
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
        return G_combine
    
    def save_graph(self, save_path, G):
        nx.drawing.nx_agraph.write_dot(G, save_path)
        ic(save_path)


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
    build_graph_from_file_code()