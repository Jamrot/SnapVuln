import networkx as nx
import copy
import queue as Queue
from icecream import ic
import re
import logging
logger = logging.getLogger(__name__)

ic.configureOutput(includeContext=True)

class Slicer:
    def __init__(self, node_graph_path, edge_graph_path):
        self.G_node = self.__read_graph(node_graph_path)
        self.G_edge = self.__read_graph(edge_graph_path)
    
    def __read_graph(self, graph_path):
        G = nx.drawing.nx_agraph.read_dot(graph_path)
        return G


    def __get_criterion_node(self, criterion_linenum, nodes):
        ## criterion location (line number)
        criterions = []
        for node in nodes:
            node_location = node['location']
            if node_location and int(node_location) == int(criterion_linenum):
                criterions.append(node)
        
        if len(criterions) == 0:
            ic('no criterion node', criterion_linenum)
            logger.error("[Slicer] No criterion node: %s", criterion_linenum)
        
        logger.info("[Slicer] criterions: %s", criterions)
        return criterions

    
    def build_slice(self, criterion_linenum, direction, g_type, depth='file'):     
        nodes, edges = self.get_nodes_and_edges()
        criterions = self.__get_criterion_node(criterion_linenum, nodes)
        criterion_slices = []
        for criterion in criterions:
            criterion_slice = {'criterion':criterion, 'nodes':[], 'edges':[]}
            graph_nodes, graph_edges = self.get_graph(nodes, edges, g_type, depth)

            if direction=='forward':
                slice_nodes = self.forward_slice(criterion, graph_nodes, graph_edges)
            elif direction=='backward':
                slice_nodes = self.backward_slice(criterion, graph_nodes, graph_edges)
            elif direction=='bid':
                slice_nodes = self.bid_slice(criterion, graph_nodes, graph_edges)
            else:
                ic('unknown direction:', direction)
                logger.warning("[Slicer] No such direction: %s", direction)
                raise Exception("No such direction: %s"%direction)
            
            slice_nodes, slice_edges = self.get_subgraph_nodes_edges(slice_nodes, graph_edges)
            if len(slice_edges) == 0 or len(slice_nodes) == 1:
                ic('no slice edges or nodes', criterion)
                logger.warning("[Slicer] No slice edges or nodes: %s", criterion)
                continue
            criterion_slice['nodes'] = slice_nodes
            criterion_slice['edges'] = slice_edges
            criterion_slices.append(criterion_slice)
        
        criterion_graph = self.__generate_subgraph(criterion_slices)
        return criterion_graph
    

    def __generate_subgraph(self, nodes_and_edges:list):
        G_sub = nx.DiGraph()
        for nodes_edges in nodes_and_edges:
            nodes = nodes_edges['nodes']
            edges = nodes_edges['edges']
            for node in nodes:
                G_sub.add_node(node['id'], **node)
            for edge in edges:
                G_sub.add_edge(edge['front'], edge['rear'], **edge)
        return G_sub


    def save_graph(self, G, save_path):
        nx.drawing.nx_agraph.write_dot(G, save_path)
        ic(save_path)
        logger.info("[Slicer] Save graph to: %s", save_path)
    
    def get_nodes_and_edges(self):
        G_graph = self.G_node
        G_edge = self.G_edge
        nodes, edges = [], []
        for node in G_graph.nodes(data=True):
            node_id = node[0]
            # node_code = node[1]['CODE'] if 'CODE' in node[1] else ''
            node_location = node[1]['LINE_NUMBER'] if 'LINE_NUMBER' in node[1] else ''
            # node_name = node[1]['NAME'] if 'NAME' in node[1] else ''
            # node_type = node[1]['label']
            new_node = node[1]
            new_node_type = self.__get_my_node_type(new_node)            
            new_node['id'] = node_id
            new_node['location'] = node_location
            new_node['type'] = new_node_type

            nodes.append(new_node)
        
        for edge in G_edge.edges(data=True):
            node1 = edge[0]
            node2 = edge[1]
            edge_type = edge[2]['label'].split(':')[0]
            edge_var = edge[2]['label'].split(':')[-1].strip() if ':' in edge[2]['label'] else edge[2].get('VARIABLE', '')
            if self.__skip_edge(edge, edge_type, edge_var):
                continue
            if edge_type in ['REF']:
                edges.append({'front': node2, 'rear': node1, 'type': edge_type, 'variable': edge_var})
            else:
                edges.append({'front': node1, 'rear': node2, 'type': edge_type, 'variable': edge_var})

        return nodes, edges

    def __skip_edge(self, edge, edge_type, edge_var):
        """skip the edge with NULL reaching def"""
        if edge_type=="REACHING_DEF" and edge_var=='NULL':
            # ic('skip edge with NULL reaching def', edge)
            logger.warning("[Slicer] Skip edge with 'NULL' variable in REACHING_DEF edge: %s", edge)
            return True
        return False


    def __get_my_node_type(self, node):
        """
        ### declaration
        'METHOD': method declaration
        'PARAM': formal parameter
        'LOCAL': local variable, CODE: local variable declaration without initialization            
        ### expression
        'BLOCK': 
        'CALL': function/method/procedure call
            - '<operator>': 'OPERATOR'
            - 'CALLEE': callee
        'CONTROL_STRUCTURE': 
        'FIELD_IDENTIFIER': the field accessed in a field access, e.g., in `a.b`, it represents `b`.
        'IDENTIFIER': an identifier as used when referring to a variable by name
        'LITERAL': literal such as an integer or string constant
        'METHOD_REF': 作为参数传入call的method
        'RETURNSTATE': return instruction, e.g., `return x`.
        'TYPE_REF': reference to a type
        'UNKNOWN': 
        ### node
        'METHOD_RETURN': CFG_NODE, formal return parameters, type name in `TYPE_FULL_NAME`.
        'JUMP_LABEL': AST_NODE, control structures GOTO and LABEL
        'JUMP_TARGET': AST_NODE / CFG_NODE, location in the code that has been specifically marked as the target of a jump
        
        """
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
            # ic('unknown node type:', node_type)
            logger.warning('unknown node type: %s, node: %s', node_type, node)
            my_node_type = node_type

        if my_node_type == 'CALL' and 'METHOD_FULL_NAME' in node:
            node_name = node['METHOD_FULL_NAME']
            if '<operator>' in node_name:
                my_node_type = MY_TYPE_LIST['<operator>']
            else:
                my_node_type = 'CALLEE'
            
        return my_node_type


    def get_graph(self, nodes, edges, g_type, depth="file"):
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


    def get_dfg_graph(self, nodes, edges):
        # TODO
        ddg_nodes, ddg_edges = self.get_graph(nodes, edges, 'ddg')
        tgt_nodes_edges = {}
        tmp_nodes = {}
        for edge in ddg_edges:
            edge_type = edge['type']
            front = edge['front']
            rear = edge['rear']
            # if edge_type == 'REACHING_DEF':
            #     variable = edge['variable'] if 'variable' in edge else ''
            # elif edge_type == 'DDG':
            #     variable = 'DDG'
            # else:
            #     print('unknown edge type:', edge_type)
            #     continue
            
            variable = edge['variable'] if 'variable' in edge else 'DDG'
            if variable not in tgt_nodes_edges:
                tgt_nodes_edges[variable] = {'nodes':[], 'edges':[]}
                tmp_nodes[variable] = set()
            
            tgt_nodes_edges[variable]['edges'].append(edge)
            tmp_nodes[variable].update([front, rear])

        for node in ddg_nodes:
            for variable in tmp_nodes:
                if node['id'] in tmp_nodes[variable]:
                    tgt_nodes_edges[variable]['nodes'].append(node)

        return tgt_nodes_edges


    def forward_slice(self, criterion, nodes, edges):
        slice_nodes = []
        visited = set()
        q = Queue.Queue()
        q.put(criterion)
        while not q.empty():
            current_node = q.get()
            slice_nodes.append(current_node)
            forward_nodes_list = self.__get_forward_nodes(current_node, nodes, edges)
            for forward_node in forward_nodes_list:
                if forward_node['id'] not in visited:
                    visited.add(forward_node['id'])
                    q.put(forward_node)
        return slice_nodes


    def backward_slice(self, criterion, nodes, edges):
        slice_nodes = []
        visited = set()
        q = Queue.Queue()
        q.put(criterion)
        while not q.empty():
            u = q.get()
            slice_nodes.append(u)
            g = self.__get_backward_nodes(u, nodes, edges)
            for v in g:
                if v['id'] not in visited:
                    visited.add(v['id'])
                    q.put(v)
        return slice_nodes
        

    def bid_slice(self, criterion, nodes, edges):
        slice_nodes = []
        rb = self.forward_slice(criterion, nodes, edges)
        rf = self.backward_slice(criterion, nodes, edges)
        for r in rb:
            if r not in slice_nodes:
                slice_nodes.append(r)
        for r in rf:
            if r not in slice_nodes:
                slice_nodes.append(r)
        return slice_nodes


    def __get_forward_nodes(self, node, nodes, edges):
        forward_nodes_id = []
        node_id = node['id']

        for edge in edges:
            if edge['front'] == node_id:
                forward_nodes_id.append(edge['rear'])

        forward_nodes = [node for node in nodes if node['id'] in forward_nodes_id]
        return forward_nodes


    def __get_backward_nodes(self, node, nodes, edges):
        backward_nodes_id = []
        node_id = node['id']

        for edge in edges:
            if edge['rear'] == node_id:
                backward_nodes_id.append(edge['front'])
                
        backward_nodes = [node for node in nodes if node['id'] in backward_nodes_id]
        return backward_nodes


    def get_subgraph_nodes_edges(self, _nodes, _edges):
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


def test():
    code_filepath = 'my-everthing/data/code/file_code_old-97bf6f81_145.c'
    # file_code_old-97bf6f81_145.c
    filename_pattern = r'file_code_old-(\w+)_(\d+).c'
    # extract info based on filename_pattern
    regex_result = re.search(filename_pattern, code_filepath)
    if not regex_result:
        ic('no commit id or line number')
        return
    commit_id = regex_result.group(1)
    criterion_linenum = regex_result.group(2)
    node_graph_path = 'my-everthing/data/graph/file_code_old-97bf6f81_145.c/dump/file_code_old-97bf6f81_145.c/_global_.dot'
    edge_graph_path = 'tmp_all/export.dot'
    slicer = Slicer(node_graph_path=edge_graph_path, edge_graph_path=edge_graph_path)
    slice_ = slicer.build_slice(criterion_linenum, 'backward', 'ddg', 'file')
    save_path = 'tmp_slice.dot'
    slicer.save_graph(slice_, save_path)

if __name__ == '__main__':
    test()