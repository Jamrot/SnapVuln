import networkx as nx
import time


def read_graph(graph_path):
    G = nx.drawing.nx_agraph.read_dot(graph_path)
    return G

def get_nodes(G):
    return G.nodes()


def get_criterion_node(G_graph, criterion_linenum):
    ## criterion location (line number)
    criterion_nodes = []
    for node in G_graph.nodes(data=True):
        node_location = node[1]['LINE_NUMBER'] if 'LINE_NUMBER' in node[1] else ''
        if node_location and int(node_location) == int(criterion_linenum):
            criterion_nodes.append(node)
    return criterion_nodes


def get_type_graph(G_graph, g_type, depth="file"):
    # call_graph: 'ARGUMENT', 'RECEIVER', 'CALL
    if g_type == 'ast':
        edge_type_list = ['AST']
    elif g_type == 'pdg':
        edge_type_list = ['PDG', 'DDG', 'REACHING_DEF', 'REF', 'CDG'] # , 'ARGUMENT', 'RECEIVER', 'DOMINATE'
    elif g_type == 'ddg': 
        edge_type_list = ['DDG', 'REACHING_DEF', 'REF'] # , 'ARGUMENT', 'RECEIVER'
    elif g_type == 'cdg':
        edge_type_list = ['CDG'] # , 'DOMINATE'
    elif g_type == 'cfg':
        edge_type_list = ['CFG']
    # elif g_type == 'dfg': # NO data flow edge
    #     edge_type_list = ['REACHING_DEF', 'DDG', 'REF', 'CALL']
    #     # return get_dfg_graph(nodes, edges)
    else:
        raise Exception("No such graph type: %s"%g_type)
    
    if not depth=="function":
        edge_type_list.append('CALL')

    if isinstance(G_graph, nx.MultiGraph) or isinstance(G_graph, nx.MultiDiGraph):
        

        edges_of_type = [(u, v, k) for u, v, k, d in G_graph.edges(data=True, keys=True) if d['label'] in edge_type_list]
    else:
        edges_of_type = [(u, v) for u, v, d in G_graph.edges(data=True) if d['label'] in edge_type_list]

    G_type_graph = G_graph.edge_subgraph(edges_of_type).copy()
    
    return G_type_graph


import queue
def forward_slice(G_graph, criterion_nodes):
    slice_nodes = set()
    q = queue.Queue()

    for node in criterion_nodes:
        q.put(node)

    while not q.empty():
        current_node = q.get()
        current_node_id = current_node[0]

        if not G_graph.has_node(current_node_id):
            print(f"???????Node {current_node_id} not in graph")
            continue

        if current_node_id not in slice_nodes:
            slice_nodes.add(current_node_id)

            successors = G_graph.successors(current_node_id)
            for successor in successors:
                if successor not in slice_nodes:
                    q.put((successor,))

    G_slice = G_graph.subgraph(slice_nodes).copy()
    return G_slice


def test_graph_time(start_time):
    graph_path = 'my-everthing/data/test/0844370f/module-0844370f-net_tls.graph/graph-0844370f-tls_strp_copyin-363-all_filename.dot'
    criterion_linenum = 363
    G_graph = read_graph(graph_path=graph_path)
    tmp_time = time.time() - start_time
    print(f"read graph: {tmp_time}")

    criterion_nodes = get_criterion_node(G_graph=G_graph, criterion_linenum=criterion_linenum)
    tmp_time = time.time() - start_time
    print(f"get criterion node: {tmp_time}")

    G_type_graph = get_type_graph(G_graph=G_graph, g_type='pdg', depth='function')
    tmp_time = time.time() - start_time
    print(f"get type graph: {tmp_time}")

    for criterion_node in criterion_nodes:
        if not G_type_graph.has_node(criterion_node[0]):
            print(f"Criterion node {criterion_node[0]} not in graph")
            continue
        criterion_slice = {'criterion':criterion_node, 'nodes':[], 'edges':[]}        
        G_slice = forward_slice(G_graph=G_type_graph, criterion_nodes=criterion_nodes)
        tmp_time = time.time() - start_time
        print(f"backward slice: {tmp_time}")

if __name__ == '__main__':
    start_time = time.time()
    print(f"Start testing graph time: {start_time}")
    test_graph_time(start_time=start_time)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Program executed in {elapsed_time:.2f} seconds")