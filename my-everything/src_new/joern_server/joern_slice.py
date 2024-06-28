import networkx as nx
import queue
import os
import subprocess
import time
import requests
import re
from collections import deque

import logging
# from log_config.log_config import setup_logging
# log_filename = os.path.join(os.path.dirname(__file__), 'log_joern_slicer.log')
# setup_logging(log_filename=log_filename)
logger = logging.getLogger(__name__)
# output log in concle
logging.basicConfig(level=logging.INFO)


from cpgqls_client import CPGQLSClient, import_code_query, workspace_query


class Joern_Slicer:
    def __init__(self, server_endpoint="localhost:8081"):
        self.client = CPGQLSClient(server_endpoint)


    def start_joern_server(self):
        cmd = [
            "joern", 
            "--server", 
            "--server-host", "localhost", 
            "--server-port", "8081", 
        ]        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Start Joern server with command: {' '.join(cmd)}")
        return process


    def joern_import_code(self, code_path, project_name):
        query = import_code_query(path=code_path, project_name=project_name)
        result = self.client.execute(query)
        logger.info("importCode query result: %s", result['stdout'])


    def joern_query(self, query):
        res = self.client.execute(query)
        result = res['stdout']
        logger.debug("Query result: %s", result)
        clean_result = self._clean_ansi_escape(result)
        logger.debug("Cleaned query result: %s", clean_result)
        return clean_result


    def _clean_ansi_escape(self, text):
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)

    def _nodeList_to_list(self, clean_result):
        clean_result = clean_result.split('=')[1].strip()
        clean_result = re.sub(r'(\d+)L', r'\1', clean_result)
        clean_result = clean_result.replace('List(', '[').replace(')', ']')
        return eval(clean_result)


    def joern_get_criterion_node(self, criterion_linenum, filename):
        """query to get all related nodes of criterion_linenum in filename"""
        query = f'cpg.file.name("{filename}").ast.lineNumber({criterion_linenum}).id.l'
        result = self.joern_query(query)
        logger.debug("extracted criterion node: %s", result)
        node_ids = self._nodeList_to_list(result)
        logger.debug("extracted criterion node_ids: %s", node_ids)
        return node_ids
    

    def build_slice(self, criterion, direction, slice_graph, slice_depth):
        criterion_linenum = criterion.get("criterion").get("line")
        criterion_modification = criterion.get("modification")
        if criterion_modification == "DELETE":
            filename = criterion.get("file_path").get("old")
        elif criterion_modification == "ADD":
            filename = criterion.get("file_path").get("new")

        criterion_node_ids = self.joern_get_criterion_node(criterion_linenum, filename)
        if not criterion_node_ids:
            logger.error(f"[Slice failed] Cannot find criterion node, No node in criterion_linenum: {criterion_linenum}, filename: {filename}")
            return None
        
        edge_type_list = self.get_edge_type_list(slice_graph, slice_depth)
        
        if direction=='forward':
            slice_nodes = self.forward_slice(criterion_node_ids, edge_type_list)
        elif direction=='backward':
            slice_nodes = self.backward_slice(criterion_node_ids, edge_type_list)
        elif direction=='bidirectional':
            slice_nodes = self.bid_slice(criterion_node_ids, edge_type_list)
        else:
            logger.error(f"[Slice failed] Invalid direction: {direction}")
            return None

        return slice_nodes

    
    def get_edge_type_list(self, graph_type, depth="file"):
        # call_graph: 'ARGUMENT', 'RECEIVER', 'CALL
        if graph_type == 'ast':
            edge_type_list = ['AST']
        elif graph_type == 'pdg':
            edge_type_list = ['PDG', 'DDG', 'REACHING_DEF', 'REF', 'CDG'] # , 'ARGUMENT', 'RECEIVER', 'DOMINATE'
        elif graph_type == 'ddg': 
            edge_type_list = ['DDG', 'REACHING_DEF', 'REF'] # , 'ARGUMENT', 'RECEIVER'
        elif graph_type == 'cdg':
            edge_type_list = ['CDG'] # , 'DOMINATE'
        elif graph_type == 'cfg':
            edge_type_list = ['CFG']
        # elif g_type == 'dfg': # NO data flow edge
        #     edge_type_list = ['REACHING_DEF', 'DDG', 'REF', 'CALL']
        #     # return get_dfg_graph(nodes, edges)
        else:
            raise Exception("No such graph type: %s"%graph_type)
        
        if not depth=="function":
            edge_type_list.append('CALL')

        return edge_type_list


    def get_node_file(self, node_id):
        current_node_id = node_id
        while True:
            query = f'cpg.id({current_node_id}).in("AST").id.l'
            result = self.joern_query(query)
            parent_ids = self._nodeList_to_list(result) if 'List(' in result else []

            if not parent_ids:
                logger.warning(f"Cannot find parent node of node_id: {current_node_id}")
                break

            current_node_id = parent_ids[0]
            
            query = f'cpg.id({current_node_id}).label.l'
            result = self.joern_query(query)
            labels = self._nodeList_to_list(result) if 'List(' in result else []

            if 'FILE' in labels:
                query = f'cpg.id({current_node_id}).property("NAME").l'
                result = self.joern_query(query)
                file_names = self._nodeList_to_list(result) if 'List(' in result else []
                if len(file_names) > 1:
                    logger.error(f"More than one file name found for node_id: {current_node_id}")
                return file_names[0] if file_names else None

        return None


    def get_nodes_file(self, node_id_list)->dict:
        """
        Return: file_map = {filename: [node_id1, node_id2, ...]}
        """
        file_map = {}

        for node_id in node_id_list:
            visited_node_set = set()
            queue = deque([node_id])         

            while queue:
                current_node_id = queue.popleft()
                visited_node_set.add(current_node_id)

                # check whether the current node is in file_map
                found_in_file_map = False
                for file in file_map:
                    file_node_set = file_map[file]
                    if current_node_id in file_node_set:
                        # add visited_node_list to file_map
                        file_node_set.update(visited_node_set)
                        file_map[file] = file_node_set
                        found_in_file_map = True
                        break
                
                if found_in_file_map:
                    continue
                
                # check whether the current node is a file node
                query = f'cpg.id({current_node_id}).label.l'
                result = self.joern_query(query)
                labels = self._nodeList_to_list(result) if 'List(' in result else []                

                if 'FILE' in labels:
                    query = f'cpg.id({current_node_id}).property("NAME").l'
                    result = self.joern_query(query)
                    file_names = self._nodeList_to_list(result) if 'List(' in result else []

                    if not file_names:
                        logger.warning(f"No file name found for node_id: {current_node_id}")
                        continue
                    if len(file_names) > 1:
                        logger.warning(f"More than one file name found for node_id: {current_node_id}")                 
                    
                    filename = file_names[0]
                    if filename in file_map:
                        file_map[filename].update(visited_node_set)
                    else:
                        file_map[filename] = visited_node_set
                    break

                # current node is not a file node, get parent node
                query = f'cpg.id({current_node_id}).in("AST").id.l'
                result = self.joern_query(query)
                parent_ids = self._nodeList_to_list(result) if 'List(' in result else []
                if not parent_ids:
                    logger.warning(f"Cannot find parent node of node_id: {current_node_id}")
                    break
                if len(parent_ids) > 1:
                    logger.warning(f"More than one parent node found for node_id: {current_node_id}")

                queue.extend(parent_ids)       

        for file in file_map:
            file_map[file] = list(file_map[file])   

        return file_map
    
    
    def backward_slice(self, node_ids, edge_type_list):
        """query to get backward slice of node_id"""
        slice_nodes = set()
        q = queue.Queue()
        for node_id in node_ids:
            q.put(node_id)

        while not q.empty():
            current_node_id = q.get()

            if current_node_id not in slice_nodes:
                slice_nodes.add(current_node_id)

                # get all nodes that have an in edge to the node_id
                for edge_type in edge_type_list:
                    query = f'cpg.id({current_node_id}).inE("{edge_type}").outV.id.l'
                    result = self.joern_query(query)
                    logger.debug("Backward slice query: %s", query)
                    logger.debug("Backward slice result: %s", result)
                    pred_node_ids = self._nodeList_to_list(result)

                    for pred_node_id in pred_node_ids:
                        if pred_node_id not in slice_nodes:
                            q.put(pred_node_id)
            
        return slice_nodes


    def forward_slice(self, node_ids, edge_type_list):
        """query to get forward slice of node_id"""
        slice_nodes = set()
        q = queue.Queue()
        for node_id in node_ids:
            q.put(node_id)

        while not q.empty():
            current_node_id = q.get()

            if current_node_id not in slice_nodes:
                slice_nodes.add(current_node_id)

                # get all nodes that have an out edge from the node_id
                for edge_type in edge_type_list:
                    query = f'cpg.id({current_node_id}).outE("{edge_type}").inV.id.l'
                    result = self.joern_query(query)
                    logger.debug("Forward slice query: %s", query)
                    logger.debug("Forward slice result: %s", result)
                    succ_node_ids = self._nodeList_to_list(result)

                    for succ_node_id in succ_node_ids:
                        if succ_node_id not in slice_nodes:
                            q.put(succ_node_id)
            
        return slice_nodes
    
    
    def bid_slice(self, node_ids, edge_type_list):
        """query to get bid slice of node_id"""
        slice_nodes = set()
        
        slice_nodes.update(self.forward_slice(node_ids, edge_type_list))
        slice_nodes.update(self.backward_slice(node_ids, edge_type_list))

        return slice_nodes


    def get_node_property(self, node_id):
        query = f'cpg.id({node_id}).propertiesMap.l'
        result = self.joern_query(query)
        logger.debug("node properties: %s", result)
        # TODO: parse result
        # TODO: get node filename
        return result



def test():
    code_filepath = '/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/code_old/net/ceph/messenger_v2.c'
    server_endpoint = "localhost:8081"
    slicer = Joern_Slicer(server_endpoint=server_endpoint)
    slicer.start_joern_server()
    project_name = 'my-test'
    slicer.joern_import_code(code_filepath, project_name)
    graph_type = "ddg"
    # filenames = slicer.get_node_file(node_id)
    criterion = {
        "criterion": {
        "line": 532,
        "code": "\tif (desc->fd_lens[0] > CEPH_MSG_MAX_CONTROL_LEN) {"
        },
        "commit_id": "a282a2f10539dce2aa619e71e1817570d557fc97",
        "version": {
        "old": "06c2afb862f9da8dc5efa4b6076a0e48c3fbaaa5",
        "new": "a282a2f10539dce2aa619e71e1817570d557fc97"
        },
        "file_path": {
        "old": "messenger_v2.c",
        "new": "net/ceph/messenger_v2.c"
        },
        "func_name": "decode_preamble",
        "func_line": {
        "start": 501,
        "end": 561
        },
        "modification": "DELETE",
        "direction": "backward",
        "graph": "ddg",
        "save_root": "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f",
        "save_filename_base": "a282a2f-decode_preamble-532-DELETE",
        "save_file_code_filepath": "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/code_old/net/ceph/messenger_v2.c",
        "save_module_dirpath": "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/code_old/net/ceph"
    }
    slice_nodes = slicer.build_slice(criterion, 'backward', graph_type, 'file')
    logger.info("backward slice: %s", slice_nodes)
    # # get code of slice_nodes
    # query = f'cpg.id({node_id}).code'
    # result = slicer.joern_query(query)
    # logger.info("code of slice node: %s", result)
    # print(filenames)
    # if filenames:
    #     exit()


if __name__ == '__main__':
    test()