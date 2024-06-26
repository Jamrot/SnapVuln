from joern.all import JoernSteps
# import networkx as nx
import graphviz
import subprocess
import threading
import time
from tqdm import tqdm

"""
joern 0.3.1 https://joern.readthedocs.io
### edges
1) edge types: 'IS_FUNCTION_OF_AST', 'IS_AST_PARENT', 'FLOWS_TO', 'DEF', 'REACHES', 'POST_DOM', 'USE', 'CONTROLS'
2) get edge type: edge.type
3) AST: IS_AST_PARENT, IS_FUNCTION_OF_AST, CFG: FLOWS_TO, DDG: REACHES, CDG: CONTROLS, DEF-USE: DEF, USE
"""


def start_neo4j():
    def run_neo4j():
        subprocess.Popen(['neo4j', 'console'])

    thread = threading.Thread(target=run_neo4j)
    thread.daemon = True
    thread.start()
    print("Starting Neo4j...")
    time.sleep(3)

def build_cpg():
    start_neo4j()

    joern_db = JoernSteps()
    joern_db.setGraphDbURL('http://localhost:7474/db/data/')
    joern_db.connectToDatabase()
    print("Successfully connected to the Joern database.")
    
    all_func_node = getALLFuncNode(joern_db)
    g = graphviz.Digraph(strict=False)
    for node in tqdm(all_func_node, desc="Processing functions"):
        func_id = node._id
        allEdges = getALLEdges(joern_db, func_id)
        g = drawGraph(g, allEdges, node, 'pdg')
    
    g.save('pdg.dot')
    print("Graph written to pdg.dot")

def drawGraph(graph, edges, func_entry_node, graph_type):
    func_id = func_entry_node._id

    for edge in edges:
        if edge.start_node.properties['code'] == 'ENTRY':
            startNode = str(edge.start_node.properties['functionId'])
        else:
            startNode = str(edge.start_node._id)

        if edge.start_node.properties['code'] == 'ERROR':
            continue

        if not isNodeExist(graph, startNode):
            if edge.start_node.properties['code'] == 'ENTRY':
                node_prop = {
                    'label': func_entry_node.properties['name'],
                    'type': func_entry_node.properties['type'],
                    'location': func_entry_node.properties['location'],
                    'functionId': str(edge.start_node.properties['functionId'])
                }
            else:
                node_prop = {
                    'label': edge.start_node.properties['code'],
                    'type': edge.start_node.properties['type'],
                    'location': edge.start_node.properties['location'],
                    'functionId': str(edge.start_node.properties['functionId'])
                }
            graph.node(startNode, **node_prop)

        endNode = str(edge.end_node._id)
        if not isNodeExist(graph, endNode):
            if graph_type == 'pdg' and edge.end_node.properties['code'] == 'EXIT':
                continue

            if edge.end_node.properties['code'] == 'ERROR':
                continue

            node_prop = {
                'label': edge.end_node.properties['code'],
                'type': edge.end_node.properties['type'],
                'location': edge.end_node.properties['location'],
                'functionId': str(edge.end_node.properties['functionId'])
            }
            graph.node(endNode, **node_prop)

        if graph_type == 'pdg':
            edge_prop = {'var': edge.properties['var']}
        else:
            edge_prop = {'var': edge.properties['flowLabel']}    

        edge_type = {'label': edge.type, 'variable': edge_prop['var']}
        graph.edge(startNode, endNode, **edge_type)

    return graph


def isNodeExist(g, nodeName):
    # return g.has_node(nodeName)
    return nodeName in g.source


def getALLFuncNode(db):
    query_str = "queryNodeIndex('type:Function')"
    results = db.runGremlinQuery(query_str)
    return results


def getALLEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE()""" % (func_id)
    allEdges = db.runGremlinQuery(query_str)
    return allEdges

def getASTEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('IS_AST_PARENT', 'IS_FUNCTION_OF_AST')""" % (func_id)
    astEdges = db.runGremlinQuery(query_str)
    return astEdges


def getDDGEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('REACHES')""" % (func_id)
    ddgEdges = db.runGremlinQuery(query_str)
    return ddgEdges


def getCDGEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('CONTROLS')""" % (func_id)
    cdgEdges = db.runGremlinQuery(query_str)
    return cdgEdges


def getCFGEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('FLOWS_TO', 'IS_FUNCTION_OF_CFG')""" % (func_id)
    cfgEdges = db.runGremlinQuery(query_str)
    return cfgEdges

def getDFGEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('DEF', 'USE')""" % (func_id)
    dfgEdges = db.runGremlinQuery(query_str)
    return dfgEdges

if __name__=="__main__":
    build_cpg()