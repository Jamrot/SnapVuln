import networkx as nx
import queue
import re
import copy

import logging
logger = logging.getLogger(__name__)


class Slicer:
    def __init__(self, G_graph):
        self.G_graph = G_graph
    
    # def read_graph(self, graph_path):
    #     G = nx.drawing.nx_agraph.read_dot(graph_path)
    #     return G


    def __get_criterion_node(self, criterion_linenum):
        ## criterion location (line number)
        criterion_nodes = []
        for node in self.G_graph.nodes(data=True):
            node_location = node[1]['LINE_NUMBER'] if 'LINE_NUMBER' in node[1] else ''
            # if not node_location:
            #     continue
            if node_location and int(node_location) == int(criterion_linenum):
                criterion_nodes.append(node)
        
        logger.debug(f"criterion_linenum matched criterion nodes: {criterion_nodes}")
        return criterion_nodes

    
    def build_slice(self, criterion_linenum, direction, g_type, depth='file'):
        criterion_nodes = self.__get_criterion_node(criterion_linenum=criterion_linenum)
        criterion_slices = []
        G_type_graph = self.get_type_graph(G_graph=self.G_graph, g_type=g_type, depth=depth)
        G_slice = nx.DiGraph()

        if len(criterion_nodes) == 0:
            logger.error(f"[Slice failed] Cannot find criterion node, No node in criterion_linenum: {criterion_linenum}")
            return G_slice

        if direction=='forward':
            G_slice_node = self.forward_slice(G_graph=G_type_graph, criterion_node=criterion_nodes)
        elif direction=='backward':
            G_slice_node = self.backward_slice(G_graph=G_type_graph, criterion_node=criterion_nodes)
        elif direction=='bidirectional':
            G_slice_node = self.bid_slice(G_graph=G_type_graph, criterion_node=criterion_nodes)
        else:
            logger.error(f"[Slice failed] Invalid direction: {direction}")
            return G_slice
        
        G_slice.add_edges_from(G_slice_node.edges(data=True))
        G_slice.add_nodes_from(G_slice_node.nodes(data=True))
         
        return G_slice
    

    def get_type_graph(self, G_graph, g_type, depth="file"):
        # call_graph: 'ARGUMENT', 'RECEIVER', 'CALL
        if g_type == 'ast':
            edge_type_list = ['AST']
        elif g_type == 'pdg':
            edge_type_list = ['PDG', 'DDG', 'REACHING_DEF', 'CDG'] # , 'ARGUMENT', 'RECEIVER', 'DOMINATE'
        elif g_type == 'ddg': 
            edge_type_list = ['DDG', 'REACHING_DEF'] # , 'ARGUMENT', 'RECEIVER'
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


        edges_of_type = []
        if isinstance(G_graph, nx.MultiGraph) or isinstance(G_graph, nx.MultiDiGraph):
            for u, v, k, d in G_graph.edges(data=True, keys=True):
                edge_label = d.get('label', '')
                edge_var = d.get('VARIABLE', '')
                if self.__skip_edge(edge_label, edge_var):
                    logger.info(f"Skip edge: {u} -> {v}, edge_label: {edge_label}, edge_var: {edge_var}")
                    continue
                if not edge_label:
                    logger.warning(f"Edge label is empty: {u} -> {v}")
                if edge_label in edge_type_list:
                    edges_of_type.append((u, v, k))
        else:
            for u, v, d in G_graph.edges(data=True):
                edge_label = d.get('label', '')
                edge_var = d.get('VARIABLE', '')
                if self.__skip_edge(edge_label, edge_var):
                    logger.info(f"Skip edge: {u} -> {v}, edge_label: {edge_label}, edge_var: {edge_var}")
                    continue
                if not edge_label:
                    logger.warning(f"Edge label is empty: {u} -> {v}")
                if edge_label in edge_type_list:
                    edges_of_type.append((u, v))

        G_type_graph = G_graph.edge_subgraph(edges_of_type).copy()
        
        return G_type_graph
    

    def __skip_edge(self, edge_label, edge_var):
        """skip the edge with NULL reaching def"""
        if edge_label=="REACHING_DEF" and edge_var=='NULL':
            return True
        return False


    def forward_slice(self, G_graph, criterion_node):
        slice_nodes = set()
        q = queue.Queue()

        print(G_graph.has_node('1189'))

        for node in criterion_node:
            q.put(node[0])

        while not q.empty():
            current_node_id = q.get()

            if not G_graph.has_node(current_node_id):
                logger.warning(f"Node not in graph: node_id - {current_node_id}, node_data - {self.G_graph.nodes[current_node_id]}")
                logger.debug(f"Node not in graph: node_id - {current_node_id}, criterion_node - {criterion_node}")
                continue

            if current_node_id not in slice_nodes:
                slice_nodes.add(current_node_id)

                successors = G_graph.successors(current_node_id)
                for succ_node_id in successors:
                    if succ_node_id not in slice_nodes:
                        q.put(succ_node_id)

        G_slice = G_graph.subgraph(slice_nodes).copy()
        return G_slice


    def backward_slice(self, G_graph, criterion_node):
        slice_nodes = set()
        q = queue.Queue()

        for node in criterion_node:
            q.put(node[0])

        while not q.empty():
            current_node_id = q.get()

            if not G_graph.has_node(current_node_id):
                logger.warning(f"[Slice] Node not in graph: node_id - {current_node_id}, node_data - {self.G_graph.nodes[current_node_id]}")
                logger.debug(f"[Slice] Node not in graph, criterion_node: {criterion_node}")
                continue

            if current_node_id not in slice_nodes:
                slice_nodes.add(current_node_id)

                pred_nodes = G_graph.predecessors(current_node_id)
                for pred_node_id in pred_nodes:
                    if pred_node_id not in slice_nodes:
                        q.put(pred_node_id)

        G_slice = G_graph.subgraph(slice_nodes).copy()
        return G_slice
    

    def bid_slice(self, G_graph, criterion_node):
        slice_nodes = set()
        
        G_slice_forward = self.forward_slice(G_graph, criterion_node)
        G_slice_backward = self.backward_slice(G_graph, criterion_node)

        slice_nodes.update(G_slice_forward.nodes)
        slice_nodes.update(G_slice_backward.nodes)

        G_slice = G_graph.subgraph(slice_nodes).copy()
        return G_slice

    def save_graph(self, G, save_path):
        nx.drawing.nx_agraph.write_dot(G, save_path)
        logger.info("Save graph to: %s", save_path)



def test():
    code_filepath = 'my-everthing/data/code/file_code_old-97bf6f81_145.c'
    # file_code_old-97bf6f81_145.c
    filename_pattern = r'file_code_old-(\w+)_(\d+).c'
    # extract info based on filename_pattern
    regex_result = re.search(filename_pattern, code_filepath)
    if not regex_result:
        print('no commit id or line number')
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