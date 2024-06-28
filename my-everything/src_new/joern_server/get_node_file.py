import networkx as nx
import queue
import os
import subprocess
import time
import requests
import re
from collections import deque

import logging
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