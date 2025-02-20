from joern.all import JoernSteps
# import networkx as nx
import graphviz
import subprocess
import threading
import time
from tqdm import tqdm
import pygraphviz as pgv
import os
import json

"""
joern 0.3.1 https://joern.readthedocs.io
### edges
1) edge types: 'IS_FUNCTION_OF_AST', 'IS_AST_PARENT', 'FLOWS_TO', 'DEF', 'REACHES', 'POST_DOM', 'USE', 'CONTROLS'
2) get edge type: edge.type
3) AST: IS_AST_PARENT, IS_FUNCTION_OF_AST, CFG: FLOWS_TO, DDG: REACHES, CDG: CONTROLS, DEF-USE: DEF, USE
"""
def init_database():
    '''
    1. set database path "/$path_to/neo4j/conf/neo4j-server.properties", "org.neo4j.server.database.location=/$path_to/.joernIndex/"
    2. delete .joernIndex in database path
    3. generate database: java -jar /$path_to/joern.jar $CODE_DIR
    4. start neo4j: /$path_to/neo4j/bin/neo4j console
    '''
    neo4j_conf_path = "/app/Tools-joern/neo4j/conf/neo4j-server.properties"
    database_path = ""
    codedir_path = ""
    # set database path
    set_database_path(neo4j_conf_path, database_path)
    # remove .joernIndex
    os.system("rm -rf {}".format(database_path))
    # generate database
    joern_path = "/app/Tools-joern/joern-0.3.1/bin/joern.jar"
    os.system("java -jar {} -outdir {} {}".format(joern_path, database_path, codedir_path))
    # start neo4j
    start_neo4j()


def set_database_path(file_path, new_db_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if line.startswith("org.neo4j.server.database.location="):
                file.write("org.neo4j.server.database.location={}\n".format(new_db_path))
            else:
                file.write(line)


def start_neo4j():
    subprocess.Popen(['/app/Tools-joern/neo4j/bin/neo4j', 'start-no-wait'])
    print("Starting Neo4j...")
    time.sleep(3)

def build_cpg():
    '''
    1. get function nodes
    2. get all nodes in the function
    3. get all edges in the function ("IS_AST_PARENT", "FLOWS_TO", "USE" & "DEF", "REACHES", "POST_DOM", "CONTROLS", "IS_FUNCTION_OF_AST", "IS_FUNCTION_OF_CFG")
    '''
    start_neo4j()

    joern_db = JoernSteps()
    joern_db.setGraphDbURL('http://localhost:7474/db/data/')
    joern_db.connectToDatabase()
    print("Successfully connected to the Joern database.")


    all_file_node = getALLFileNode(joern_db)
    print(["file {}\n".format(node._id) for node in all_file_node])
    for file_node in tqdm(all_file_node, desc="Processing files"):
        file_id = file_node._id
        func_nodes = getFileFuncNode(joern_db, file_id)
        file_path = file_node.properties['filepath']

        filepath_base = file_path.replace("func/", "dot/").replace(".c", "").replace('data_process/', 'data_process_lala/')
        if not os.path.exists(os.path.dirname(filepath_base)):
            os.makedirs(os.path.dirname(filepath_base))

        for node in tqdm(func_nodes, desc="Processing functions"):
            nodes_list = []
            edges_list = []

            g = graphviz.Digraph(strict=False)
            added_nodes = []
            func_id = node._id
            func_name = node.properties['name']
            # traverse all ast edges in the function
            astNodes = getASTNodes(joern_db, func_id)
            g, nodes_list = addNodes(g, astNodes, node, added_nodes, nodes_list)

            astEdges = getASTEdges(joern_db, func_id)
            g, edges_list = addEdges(edges_list, g, astEdges)
            cfgEdges = getCFGEdges(joern_db, func_id)
            g, edges_list = addEdges(edges_list, g, cfgEdges)
            dfgEdges = getDFGEdges(joern_db, func_id)
            g, edges_list = addEdges(edges_list, g, dfgEdges)
            ddgEdges = getDDGEdges(joern_db, func_id) # REACHES
            g, edges_list = addEdges(edges_list, g, ddgEdges)
            postdomEdges = getPOSTDOMEdges(joern_db, func_id) # POST_DOM
            g, edges_list = addEdges(edges_list, g, postdomEdges)
            cdgEdges = getCDGEdges(joern_db, func_id) # CONTROLS
            g, edges_list = addEdges(edges_list, g, cdgEdges)
            
            funcEdges = getFUNCEdges(joern_db, func_id)
            g, edges_list = addEdges(edges_list, g, funcEdges)

            nodes_list = sorted(nodes_list, key=lambda x: int(x['nodeid']))
            content = graph_to_content(nodes_list, edges_list)

            output_filepath = filepath_base + '_' + func_name + '.c.dot'
            with open(output_filepath, 'w') as f:
                f.write(content)
            
            print("Graph written to {}".format(output_filepath))


def addNodes(graph, nodes, func_node, added_nodes, nodes_list):

    func_node_id = str(func_node._id)
    func_node_prop = {
        # 'label': 'name:{name}\ntype:{type}\nnodeid:{nodeid}\n'.format(
        #     name=func_node.properties["name"],
        #     type=func_node.properties["type"],
        #     nodeid=func_node_id
        # ),
        'name': func_node.properties['name'],
        'type': func_node.properties['type'],
        'nodeid': func_node_id
    }
    if not isNodeExist(graph, func_node):
        graph.node(func_node_id)
        # graph.node(func_node_id, **func_node_prop)
        added_nodes.append(func_node_id)
        nodes_list.append(func_node_prop)

    for node in nodes:
        node_id = str(node._id).encode('unicode_escape')

        label = ""
        functionId = node.properties.get('functionId', None)
        label += 'functionId:{functionId}\n'.format(functionId=functionId) if functionId else ''
        code = node.properties.get('code', '')
        code = json.dumps(code)[1:-1]
        # code = repr(code)
        label += 'code:{code}\n'.format(code=code)
        childNum = node.properties.get('childNum', None)
        label += 'childNum:{childNum}\n'.format(childNum=childNum) if childNum else ''
        isCFGNode = node.properties.get('isCFGNode', None)
        label += 'isCFGNode:{isCFGNode}\n'.format(isCFGNode=isCFGNode) if isCFGNode else ''
        location = node.properties.get('location', None)
        label += 'location:{location}\n'.format(location=location) if location else ''
        _type = node.properties.get('type', None)
        label += 'type:{type}\n'.format(type=_type) if type else ''
        nodeid = node_id
        label += 'nodeid:{nodeid}\n'.format(nodeid=nodeid)

        node_prop = {
            # 'label': label,
            'functionId': str(functionId).encode('unicode_escape'),
            'code': code,
            # 'code': code,
            # 'name': node.properties.get('name', node_id),
            # 'location': location,
            'type': _type,
            'nodeid': str(node_id).encode('unicode_escape')
        }

        name = node.properties.get('name', None)
        if name:
            node_prop['name'] = name

        if childNum:
            node_prop['childNum'] = childNum
        
        if location:
            node_prop['location'] = location

        if isCFGNode:
            node_prop['isCFGNode'] = isCFGNode

        operator = node.properties.get('operator', None)
        if operator:
            node_prop['operator'] = operator

        if not isNodeExist(graph, node):
            graph.node(node_id)
            # graph.node(node_id, **node_prop)
            added_nodes.append(node_id)
            nodes_list.append(node_prop)
    return graph, nodes_list

def addEdges(edges_list, graph, edges):
    for edge in edges:
        startNode = str(edge.start_node._id)
        endNode = str(edge.end_node._id)
        edge_prop = {'var': edge.properties['var']}
        edge_type = {'label': edge.type, 'variable': edge_prop['var']}
        graph.edge(startNode, endNode, **edge_type)
        edges_list.append({
            'front': startNode,
            'rear': endNode,
            'type': edge.type,
        })
    return graph, edges_list


def graph_to_content(nodes, edges):
	content = 'digraph G {\n'

	node_content = ''
	for node in nodes:
		node_content = node_content + '  '+node['nodeid']+' [ label="'
		for key, value in node.items():
			node_content = node_content +str(key)+':'+str(value)+'\n'
		node_content = node_content + '" '

		for key, value in node.items():
			node_content = node_content + str(key) + '="' + str(value) + '" '
		node_content = node_content + "];\n"

	edge_content = ''
	for edge in edges:
		edge_content = edge_content + '  ' + str(edge['front']) + ' -> ' + str(edge['rear']) + ' [ label="' + str(edge['type']) + '" name="(('+ str(edge['front']) + ') : ('+str(edge['rear'])+') : '+ str(edge['type'])+')" ];\n'

	content = content + node_content + edge_content + '}'

	return content


def isNodeExist(graph, node):
    node_id = str(node._id)
    return node_id in [i.strip() for i in graph.source.split()]

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

def getALLFileNode(db):
    query_str = "queryNodeIndex('type:File')"
    results = db.runGremlinQuery(query_str)
    return results

def getFileFuncNode(db, file_id):
    # .out(IS_FILE_OF)
    # query_str = """queryNodeIndex('id:%s')""" % (file_id)
    query_str = """g.v(1).out().filter{it.type == 'Function'}"""
    results = db.runGremlinQuery(query_str)
    return results


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