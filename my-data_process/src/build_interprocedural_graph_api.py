# - coding = utf-8-#
import re
import subprocess
import os
import shutil
import time
import queue as Queue
from slice_api import *

# def get_nodes_and_edges(dotfile, mode='default'):
#     node_chunks, edge_chunks = [], []
#     regex1 = r'(  \d+ \[.*?\]\n)'
#     regex2 = r'(  \d+ \-\> \d+ .*?\]\n)'
#     if mode == 'default':
#         with open(dotfile,'r') as f:
#             fs = f.read()
#     elif mode == 'string':
#         fs = dotfile
#     else:
#         return None, None

#     node_chunks = re.findall(regex1, fs, re.S)
#     edge_chunks = re.findall(regex2, fs, re.S)

#     nodes, edges = [], []
#     type_list = []
#     for chunk in node_chunks:
#         node = {}
#         id_regex = r"(\d+) \["
#         fid_regex = r'functionId="(.*?)" ' # TODO
#         name_regex = r' NAME="(.*?)"'
#         type_regex = r'label=(.*?) '
#         code_regex = r'CODE="(.*?)" '
#         loc_regex = r'location:(\d+)' # TODO
#         childnum_regex = r'childNum:(\d+)' # TODO
#         _id = re.findall(id_regex, chunk)
#         fid = re.findall(fid_regex, chunk) # TODO
#         name = re.findall(name_regex, chunk)
#         tp = re.findall(type_regex, chunk)
#         code = re.findall(code_regex, chunk)
#         loc = re.findall(loc_regex, chunk) # TODO
#         childnum = re.findall(childnum_regex, chunk) # TODO
        
#         node['chunk'] = chunk
#         if _id != []:
#             node['ID'] = _id[0]
#         if fid != []:
#             node['functionId']=fid[0]
#         if name != []:
#             node['name']=name[0]
#         if tp != []:
#             node['type'] = tp[0]
#         if code != []:
#             node['code'] = code[0]
#         if loc != []:
#             node['location'] = loc[0]
#         if childnum != []:
#             node['childNum'] = childnum[0]

#         nodes.append(node)
    
#     for chunk in edge_chunks:
#         edge_regex = r'((\d+) \-\> (\d+) \[.*label\=(.+?)) '
#         edge_info = re.findall(edge_regex, chunk, re.S)[0]
#         edges.append({'front':edge_info[1],'rear':edge_info[2],'type':edge_info[3],'chunk':chunk})
        
#     return nodes, edges


def get_correspond_node(node, nodes, edges, g_type):
    """
    get correspond nodes with the input 'node' in the target graph

    Parameters:
        node: the target node
    
    Local Variables:
        _nodes: nodes in the target graph
        correspond_nodes_id: nodes in the target graph have code attribute
        tmp_id: the id of the examinating node
    
    Returns:

    """
    ast_nodes, ast_edges = get_graph(nodes, edges, 'ast')
    # root_nodeid_ast = [edge['front'] for edge in ast_edges if edge['type']=="AST"][0]
    root_nodeid_ast = [node['ID'] for node in ast_nodes if node['type']=="METHOD"][0] # TODO: find the root node of AST
    
    if g_type == 'cfg':
        _nodes, _ = get_graph(nodes, edges, 'cfg')
    elif g_type == 'dfg':
        _nodes, _ = get_graph(nodes, edges, 'dfg')
    elif g_type == 'pdg':
        _nodes, _ = get_graph(nodes, edges, 'pdg')
    elif g_type == 'ddg':
        _nodes, _ = get_graph(nodes, edges, 'ddg')
    elif g_type == 'cdg':
        _nodes, _ = get_graph(nodes, edges, 'cdg')
    else:
        print("no such graph: %s"%g_type)
        return None

    node_id = node['ID']
    # correspond_nodes_id = [n['ID'] for n in _nodes if 'code' in n.keys()] # nodes in the target graph have code attribute
    correspond_nodes_id = [n['ID'] for n in _nodes] 

    tmp_id = node_id
    flag = True
    while flag:
        tmp_ids = [edge['front'] for edge in ast_edges if int(edge['rear']) == int(tmp_id)] # find the parent node of tmp_id
        if len(tmp_ids) != 1: # if not find the parent node for tmp_id / the parent node is not unique , then return None
            print("Node %s not in AST (%d) ."%(node, len(tmp_ids)))
            return None

        tmp_id = tmp_ids[0] # make the tmp_id as the parent node
        if tmp_id in correspond_nodes_id: # if the parent node in correspond_nodes_id (i.e., has code attribute), then return the node
            flag = False
            break
        elif tmp_id == root_nodeid_ast: # if the parent node is the root node of AST, then return None
            print("No correspond node in %s - Node: %s [%s] " % (g_type, node['ID'], node['name']))
            return None

    _node = [node for node in _nodes if int(node['ID']) == int(tmp_id)][0]
    return _node


# def get_graph(nodes, edges, g_type):
#     if g_type == 'ast':
#         edge_type_list = ['AST']
#     elif g_type == 'pdg':
#         edge_type_list = ['REACHING_DEF', 'PDG', 'DDG', 'CDG']
#     elif g_type == 'ddg': 
#         edge_type_list = ['REACHING_DEF', 'DDG']
#     elif g_type == 'cdg':
#         edge_type_list = ['CDG']
#     elif g_type == 'cfg':
#         edge_type_list = ['CFG']
#     elif g_type == 'dfg': # TODO: cannot find the data flow edge
#         edge_type_list = ['REACHING_DEF']
#     else:
#         raise Exception("No such graph type: %s"%g_type)
    
#     tgt_nodes = []
#     tgt_edges = []

#     tmp_nodes = []
#     for edge in edges:
#         if edge['type'] in edge_type_list:
#             tgt_edges.append(edge)
#             front = edge['front']
#             rear = edge['rear']
#             if front not in tmp_nodes:
#                 tmp_nodes.append(front)
#             if rear not in tmp_nodes:
#                 tmp_nodes.append(rear)
#     for node in nodes:
#         if node['ID'] in tmp_nodes:
#             tgt_nodes.append(node)

#     return tgt_nodes, tgt_edges
