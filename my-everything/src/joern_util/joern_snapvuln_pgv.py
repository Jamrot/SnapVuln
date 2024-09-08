from joern.all import JoernSteps
import pygraphviz as pgv
import subprocess
import threading
import time
from tqdm import tqdm

def start_neo4j():
    def run_neo4j():
        subprocess.Popen(['neo4j', 'console'])

    thread = threading.Thread(target=run_neo4j)
    thread.daemon = True
    thread.start()
    print("Starting Neo4j...")
    time.sleep(3)

def build_cpg():
    '''
    1. get function nodes
    2. get all nodes in the function
    3. get all edges in the function ("IS_AST_PARENT", "FLOWS_TO", "USE" & "DEF", "REACHES", "POST_DOM", "CONTROLS", "IS_FUNCTION_OF_AST", "IS_FUNCTION_OF_CFG")
    '''
    # start_neo4j()

    joern_db = JoernSteps()
    joern_db.setGraphDbURL('http://localhost:7474/db/data/')
    joern_db.connectToDatabase()
    print("Successfully connected to the Joern database.")
    
    all_func_node = getALLFuncNode(joern_db)
    print(["function {}\n".format(node.properties['name']) for node in all_func_node])
    for node in tqdm(all_func_node, desc="Processing functions"):
        g = pgv.AGraph(strict=False, directed=True)
        added_nodes = []
        func_id = node._id
        func_name = node.properties['name']
        
        # traverse all ast edges in the function
        astNodes = getASTNodes(joern_db, func_id)
        g = addNodes(g, astNodes, node, added_nodes)

        astEdges = getASTEdges(joern_db, func_id)
        g = addEdges(g, astEdges)
        cfgEdges = getCFGEdges(joern_db, func_id)
        g = addEdges(g, cfgEdges)
        dfgEdges = getDFGEdges(joern_db, func_id)
        g = addEdges(g, dfgEdges)
        ddgEdges = getDDGEdges(joern_db, func_id) # REACHES
        g = addEdges(g, ddgEdges)
        postdomEdges = getPOSTDOMEdges(joern_db, func_id) # POST_DOM
        g = addEdges(g, postdomEdges)
        cdgEdges = getCDGEdges(joern_db, func_id) # CONTROLS
        g = addEdges(g, cdgEdges)
        
        funcEdges = getFUNCEdges(joern_db, func_id)
        g = addEdges(g, funcEdges)

        g.write('{}.dot'.format(func_name))
    
    print("Graph written to .dot files")

def addNodes(graph, nodes, func_node, added_nodes):

    func_node_id = str(func_node._id)
    func_node_label = 'name: {}\ntype: {}\nnodeid: "{}"'.format(
        func_node.properties["name"],
        func_node.properties["type"],
        func_node_id
    )

    if func_node_id not in added_nodes:
        graph.add_node(func_node_id, label=func_node_label)
        added_nodes.append(func_node_id)

    for node in nodes:
        node_id = str(node._id)

        label = ""
        functionId = node.properties.get('functionId', None)
        label += 'functionId: {}\n'.format(functionId) if functionId else ''
        code = node.properties.get('code', '')
        label += 'code: {}\n'.format(code)
        childNum = node.properties.get('childNum', None)
        label += 'childNum: {}\n'.format(childNum) if childNum else ''
        isCFGNode = node.properties.get('isCFGNode', None)
        label += 'isCFGNode: {}\n'.format(isCFGNode) if isCFGNode else ''
        location = node.properties.get('location', None)
        label += 'location: {}\n'.format(location) if location else ''
        _type = node.properties.get('type', None)
        label += 'type: {}\n'.format(_type) if _type else ''
        nodeid = node_id
        label += 'nodeid: "{}"\n'.format(nodeid)

        node_prop = {
            'label': label,
            'functionId': str(functionId).encode('unicode_escape'),
            'code': code.encode('unicode_escape'),
            'name': node.properties.get('name', node_id),
            'location': location,
            'type': _type,
            'nodeid': str(node_id).encode('unicode_escape')
        }

        if node_id not in added_nodes:
            graph.add_node(node_id, **node_prop)
            added_nodes.append(node_id)

    return graph

def addEdges(graph, edges):
    for edge in edges:
        start_node = str(edge.start_node._id)
        end_node = str(edge.end_node._id)
        edge_label = edge.type
        graph.add_edge(start_node, end_node, label=edge_label)
    return graph


def isNodeExist(graph, node):
    node_id = str(node._id)
    return node_id in graph.nodes()

def getParentsNodes(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').parents()""" % (func_id)
    parentsNodes = db.runGremlinQuery(query_str)
    return parentsNodes


def getChildrenNodes(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').children()""" % (func_id)
    childrenNodes = db.runGremlinQuery(query_str)
    return childrenNodes


def getASTNodes(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').astNodes()""" % (func_id)
    astNodes = db.runGremlinQuery(query_str)
    return astNodes

def getCFGNodes(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').statements()""" % (func_id)
    cfgNodes = db.runGremlinQuery(query_str)
    return cfgNodes

def getUseNodes(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').uses()""" % (func_id)
    symbNodes = db.runGremlinQuery(query_str)
    return symbNodes

def getDefNodes(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').defines()""" % (func_id)
    symbNodes = db.runGremlinQuery(query_str)
    return symbNodes

def getDefinitionNodes(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').definitions()""" % (func_id)
    definitionNodes = db.runGremlinQuery(query_str)
    return definitionNodes


def getALLFuncNode(db):
    query_str = "queryNodeIndex('type:Function')"
    results = db.runGremlinQuery(query_str)
    return results


def getALLEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE()""" % (func_id)
    allEdges = db.runGremlinQuery(query_str)
    return allEdges

def getFUNCEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').inE('IS_FUNCTION_OF_AST', 'IS_FUNCTION_OF_CFG')""" % (func_id)
    funcEdges = db.runGremlinQuery(query_str)
    return funcEdges

def getFUNCEdges_other(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').inE('IS_AST_PARENT', 'REACHES', 'CONTROLS', 'FLOWS_TO', 'DEF', 'USE')""" % (func_id)
    funcEdges = db.runGremlinQuery(query_str)
    return funcEdges

def getASTEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('IS_AST_PARENT')""" % (func_id)
    # query_str = """queryNodeIndex('functionId:%s').out('IS_AST_PARENT', 'IS_FUNCTION_OF_AST')""" % (func_id)
    astEdges = db.runGremlinQuery(query_str)
    return astEdges


def getDDGEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('REACHES')""" % (func_id)
    ddgEdges = db.runGremlinQuery(query_str)
    return ddgEdges

def getPOSTDOMEdges(db, func_id):
    query_str = """queryNodeIndex('functionId:%s').outE('POST_DOM')""" % (func_id)
    postdomEdges = db.runGremlinQuery(query_str)
    return postdomEdges


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