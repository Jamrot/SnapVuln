import networkx as nx

def read_graph(graph_path):
    G = nx.drawing.nx_agraph.read_dot(graph_path)
    return G

def analyze_edge():
    cpg_graph_path = "tmp_cpg/file_code_old-97bf6f81_145.c/_global_.dot"
    cpg14_graph_path = "tmp_cpg14/0-cpg.dot"
    G_cpg = read_graph(cpg_graph_path)
    G_cpg14 = read_graph(cpg14_graph_path)

    cpg14_edge = G_cpg14.edges
    cpg_edge = G_cpg.edges

    # cpg14_edges_list = []
    for edge in cpg_edge:
        front_edge = edge[0]
        rear_edge = edge[1]
        # get rear edge of front edge
        if not cpg14_edge.get(edge):
            print(edge)
            # print(cpg14_edge[edge])
            print(cpg_edge[edge])
            print('xxxx')
            continue
        print(edge)
        print(cpg_edge[edge])
        print(cpg14_edge[edge])
        if 'DDG' in cpg14_edge[edge]['label']:
            print('----')

if __name__ == '__main__':
    analyze_edge()
