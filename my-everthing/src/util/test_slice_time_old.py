import networkx as nx
import time


def read_graph(graph_path):
    G = nx.drawing.nx_agraph.read_dot(graph_path)
    return G

def get_nodes(G):
    return G.nodes()


def get_criterion_node(criterion_linenum, nodes):
    ## criterion location (line number)
    criterions = []
    for node in nodes:
        node_location = node['location']
        if node_location and int(node_location) == int(criterion_linenum):
            criterions.append(node)
    
    return criterions


def get_my_node_type(node):
        node_type = node['label']
        my_node_type = ''

        NODE_TYPE_LIST = {
            # declaration
            'METHOD': 'METHOD', # DECLARATION, method declaration
            'METHOD_PARAMETER_IN': 'PARAM', # DECLARATION, formal parameter
            'METHOD_PARAMETER_OUT': 'PARAM', # DECLARATION, MUST NOT be created by the frontend
            'LOCAL': 'LOCAL', # DECLARATION, local variable, CODE: local variable declaration without initialization            
            # expression
            'BLOCK': 'BLOCK', # EXPRESSION
            'CALL': 'CALL', # EXPRESSION, function/method/procedure call
            'CONTROL_STRUCTURE': 'CONTROL_STRUCTURE', # EXPRESSION
            'FIELD_IDENTIFIER': 'FIELD_IDENTIFIER', # EXPRESSION, the field accessed in a field access, e.g., in `a.b`, it represents `b`.
            'IDENTIFIER':'IDENTIFIER', # EXPRESSION, an identifier as used when referring to a variable by name
            'LITERAL': 'LITERAL', # EXPRESSION, literal such as an integer or string constant
            'METHOD_REF': 'METHOD_REF', # EXPRESSION, 作为参数传入call的method
            'RETURN': 'RETURNSTATE', # EXPRESSION, return instruction, e.g., `return x`.
            'TYPE_REF': 'TYPE_REF', # EXPRESSION, reference to a type
            'UNKNOWN': 'UNKNOWN', # EXPRESSION
            # node
            'METHOD_RETURN': 'METHOD_RETURN', # CFG_NODE, formal return parameters, type name in `TYPE_FULL_NAME`.
            'JUMP_LABEL': 'JUMP_LABEL', # AST_NODE, control structures GOTO and LABEL
            'JUMP_TARGET': 'JUMP_TARGET' # AST_NODE / CFG_NODE, location in the code that has been specifically marked as the target of a jump
            }

        MY_TYPE_LIST = {
            '<operator>': 'OPERATOR' # logic operations
        }
        if node_type in NODE_TYPE_LIST:
            my_node_type = NODE_TYPE_LIST[node_type]
        else:
            my_node_type = node_type

        if my_node_type == 'CALL' and 'METHOD_FULL_NAME' in node:
            node_name = node['METHOD_FULL_NAME']
            if '<operator>' in node_name:
                my_node_type = MY_TYPE_LIST['<operator>']
            else:
                my_node_type = 'CALLEE'
            
        return my_node_type


def get_nodes_and_edges(G_graph):
    G_edge = G_graph
    nodes, edges = [], []
    for node in G_graph.nodes(data=True):
        node_id = node[0]
        # node_code = node[1]['CODE'] if 'CODE' in node[1] else ''
        node_location = node[1]['LINE_NUMBER'] if 'LINE_NUMBER' in node[1] else ''
        # node_name = node[1]['NAME'] if 'NAME' in node[1] else ''
        # node_type = node[1]['label']
        new_node = node[1]
        new_node_type = get_my_node_type(new_node)            
        new_node['id'] = node_id
        new_node['location'] = node_location
        new_node['type'] = new_node_type

        nodes.append(new_node)
    
    for edge in G_edge.edges(data=True):
        node1 = edge[0]
        node2 = edge[1]
        edge_type = edge[2]['label'].split(':')[0]
        edge_var = edge[2]['label'].split(':')[-1].strip() if ':' in edge[2]['label'] else edge[2].get('VARIABLE', '')
        if edge_type=="REACHING_DEF" and edge_var=='NULL':
            continue
        if edge_type in ['REF']:
            edges.append({'front': node2, 'rear': node1, 'type': edge_type, 'variable': edge_var})
        else:
            edges.append({'front': node1, 'rear': node2, 'type': edge_type, 'variable': edge_var})

    return nodes, edges


def get_graph(nodes, edges, g_type, depth="file"):
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

    tgt_nodes = []
    tgt_edges = []

    tmp_nodes = []
    for edge in edges:
        if edge['type'] in edge_type_list:
            tgt_edges.append(edge)
            front = edge['front']
            rear = edge['rear']
            if front not in tmp_nodes:
                tmp_nodes.append(front)
            if rear not in tmp_nodes:
                tmp_nodes.append(rear)
    for node in nodes:
        if node['id'] in tmp_nodes:
            tgt_nodes.append(node)

    return tgt_nodes, tgt_edges


import queue as Queue
def backward_slice(criterion, nodes, edges):
    slice_nodes = []
    visited = set()
    q = Queue.Queue()
    q.put(criterion)
    while not q.empty():
        u = q.get()
        slice_nodes.append(u)
        g = __get_backward_nodes(u, nodes, edges)
        for v in g:
            if v['id'] not in visited:
                visited.add(v['id'])
                q.put(v)
    return slice_nodes


def __get_backward_nodes(node, nodes, edges):
    backward_nodes_id = []
    node_id = node['id']

    for edge in edges:
        if edge['rear'] == node_id:
            backward_nodes_id.append(edge['front'])
            
    backward_nodes = [node for node in nodes if node['id'] in backward_nodes_id]
    return backward_nodes


def test_graph_time(start_time):
    graph_path = 'my-everthing/data/test/0844370f/module-0844370f-net_tls.graph/graph-0844370f-tls_strp_copyin-363-all_filename.dot'
    criterion_linenum = 363
    G_graph = read_graph(graph_path=graph_path)
    tmp_time = time.time() - start_time
    print(f"read graph: {tmp_time}")


    nodes, edges = get_nodes_and_edges(G_graph=G_graph)
    graph_nodes, graph_edges = get_graph(nodes=nodes, edges=edges, g_type='pdg', depth='module')
    tmp_time = time.time() - start_time
    print(f"get graph: {tmp_time}")

    criterion_nodes = get_criterion_node(criterion_linenum=criterion_linenum, nodes=graph_nodes)
    tmp_time = time.time() - start_time
    print(f"get criterion node: {tmp_time}")

    for criterion_node in criterion_nodes:
        # criterion_slice = {'criterion':criterion_node, 'nodes':[], 'edges':[]}
        slice_nodes = backward_slice(criterion=criterion_node, nodes=graph_nodes, edges=graph_edges)
        tmp_time = time.time() - start_time
        print(f"backward slice: {tmp_time}")

        slice_nodes, slice_edges = get_subgraph_nodes_edges(slice_nodes, graph_edges)
        tmp_time = time.time() - start_time
        print(f"get subgraph nodes and edges: {tmp_time}")


import copy
def get_subgraph_nodes_edges(_nodes, _edges):
    nodes = copy.deepcopy(_nodes)
    edges = copy.deepcopy(_edges)
    slice_nodes = []
    slice_edges = []
    slice_nodes_id = [slice_node['id'] for slice_node in nodes]
    for edge in edges:
        if edge['front'] in slice_nodes_id and edge['rear'] in slice_nodes_id:
            slice_edges.append(edge)
            if nodes[slice_nodes_id.index(edge['front'])] not in slice_nodes:
                slice_nodes.append(nodes[slice_nodes_id.index(edge['front'])])
            if nodes[slice_nodes_id.index(edge['rear'])] not in slice_nodes:
                slice_nodes.append(nodes[slice_nodes_id.index(edge['rear'])])
    return slice_nodes, slice_edges


if __name__ == '__main__':
    start_time = time.time()
    print(f"Start testing graph time: {start_time}")
    test_graph_time(start_time=start_time)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Program executed in {elapsed_time:.2f} seconds")