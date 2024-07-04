import subprocess
import os
import networkx as nx

def get_all_ddg():
    graph_dump_dir = "/app/slicing-snapvuln/my-everything/joern_test/struct_test-all"
    # graph_dump_dir = "/app/slicing-snapvuln/my-everything/joern_test/make_output"
    G_combine = nx.DiGraph()
    for graph_file in os.listdir(graph_dump_dir):
        if not graph_file.endswith(".dot"):
            continue
        graph_file_path = os.path.join(graph_dump_dir, graph_file)
        G_graph = nx.drawing.nx_agraph.read_dot(graph_file_path)

        # Get all nodes and edges related to DDG
        ddg_edges = []
        if isinstance(G_graph, nx.MultiGraph) or isinstance(G_graph, nx.MultiDiGraph):
            for u, v, k, d in G_graph.edges(data=True, keys=True):
                edge_label = d.get('label', '')
                if check_label(edge_label):
                    ddg_edges.append((u, v, k, d))
        else:
            for u, v, d in G_graph.edges(data=True):
                edge_label = d.get('label', '')
                if check_label(edge_label):
                    ddg_edges.append((u, v, d))

        if ddg_edges:
            # Manually add nodes and edges from G_graph to G_combine
            for u, v, *rest in ddg_edges:
                G_combine.add_node(u, **G_graph.nodes[u])
                G_combine.add_node(v, **G_graph.nodes[v])
                if len(rest) == 2:  # For MultiGraph
                    k, d = rest
                    G_combine.add_edge(u, v, key=k, **d)
                else:
                    d = rest[0]
                    G_combine.add_edge(u, v, **d)
    
    # Ensure G_combine is still a valid graph before writing to dot file
    if G_combine.number_of_nodes() > 0:
        # Write to dot file
        for node in G_combine.nodes(data=True):
            node_data = node[1]
            node_data['label'] = "\n".join([
                                        node_data.get('label').split("\n")[0], 
                                        "id:"+node[0],
                                        "name:"+node_data.get('NAME', ""),
                                        "line:"+node_data.get('LINE_NUMBER', ""),
                                        "code:"+node_data.get('CODE', ""),
                                        ])
        dot_file = os.path.join(graph_dump_dir, "export_all_ddg.dot")
        nx.drawing.nx_agraph.write_dot(G_combine, dot_file)
        pdf_file = dot_file.replace(".dot", ".pdf")
        cmd = f'dot -Tpdf {dot_file} -o {pdf_file}'
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(f'Successfully converted {dot_file} to {pdf_file}')
        else:
            print(f'Error converting {dot_file} to {pdf_file}: {result.stderr}')
    else:
        print("No valid DDG edges found to combine.")


def check_label(edge_label):
    check_list = ["DDG", "REACHING_DEF", "CALL", 'CDG']
    for check in check_list:
        if check in edge_label:
            return True


def test():
    graph_type = "all"
    source_path = "my-everything/joern_test/struct_test-multi.c"
    bin_file = f"my-everything/joern_test/struct_test-{graph_type}.bin"
    graph_dir = f"my-everything/joern_test/struct_test-{graph_type}"

    if os.path.exists(bin_file):
        os.remove(bin_file)
    cmd = f'joern-parse {source_path} -o {bin_file}'
    result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    os.system(f'rm -rf {graph_dir}')
    cmd = f'joern-export --repr {graph_type} {bin_file} --out {graph_dir}'
    result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    dot_file = os.path.join(graph_dir, "export.dot")
    # G = nx.drawing.nx_agraph.read_dot(dot_file)
    # # config label as name
    # for node in G.nodes(data=True):
    #     node_data = node[1]
    #     node_data['label'] = "\n".join(["label:"+node_data.get('label'), 
    #                                    "name:"+node_data.get('NAME', ""),
    #                                    "line:"+node_data.get('LINE_NUMBER', ""),
    #                                    "code:"+node_data.get('CODE', ""),
    #                                    ])
    # # save dot file
    # nx.drawing.nx_agraph.write_dot(G, dot_file)
    # pdf_file = source_path.replace(".c", ".dot.pdf")
    # cmd = f'dot -Tpdf {dot_file} -o {pdf_file}'
    # result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


test()
# get_all_ddg()