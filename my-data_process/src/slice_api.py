# - coding = utf-8-#
import re
import copy
from pygments.lexers.c_cpp import CLexer
import queue as Queue

NODE_TYPE_LIST = {
    'IDENTIFIER':'IDEN', 'FIELD_IDENTIFIER':'IDEN', 
    'CALL': 'CALL',                         
    'METHOD':'METHOD', 
    'METHOD_PARAMETER_IN': 'PARAM',
    'METHOD_PARAMETER_OUT': 'PARAM',
    'RETURN': 'RETURNSTATE', # actual return parameters
    'METHOD_RETURN': 'RETURNTYPE', # formal return parameters, type name in `TYPE_FULL_NAME`.
    'BLOCK':'BLOCKSTARTER',  
    'CONTROL_STRUCTURE': 'UNKNOWN', # TODO: CONTROL_STRUCTURE_TYPE
    'LOCAL':'IDENDECLSTATE', # TODO: local variable declare statement
    'LITERAL':'UNKNOWN', 
	'UNKNOWN':'UNKNOWN',
	'JUMP_TARGET':'UNKNOWN'
    }

def tokenizer(fun):
	tokens = []
	for i, j, t in CLexer().get_tokens_unprocessed(fun):
		t = camel_case_split(t)
		for subword in t:
			subword = subword.lower()
			if subword is None or str(subword).strip() == "":
				pass
			elif "Token.Comment" in str(j):
				pass
			elif "Token.Name" in str(j):
				subword = str(subword).split('_')
				tokens.extend(subword)
			else:
				tokens.append(subword)
	return tokens

def camel_case_split(identifier):
	matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
	return [m.group(0) for m in matches]

def get_nodes_and_edges(dotfile, mode='default'):
    node_chunks, edge_chunks = [], []
    # regex1 = r'(  \d+ \[.*?\]\;\n)'
    regex1 = r'(  \d+ \[.*?\]\n)'
    # regex2 = r'(  \d+ \-\> \d+ .*?\]\;\n)'
    regex2 = r'(  \d+ \-\> \d+ .*?\]\n)'
    if mode == 'default':
        with open(dotfile,'r') as f:
            fs = f.read()
    elif mode == 'string':
        fs = dotfile
    else:
        return None, None

    node_chunks = re.findall(regex1, fs, re.S)
    edge_chunks = re.findall(regex2, fs, re.S)

    nodes, edges = [], []
    type_list = []
    for chunk in node_chunks:
        node = {}
        id_regex = r"(\d+) \["
        # fid_regex = r'functionId="(.*?)" '
        name_regex = r' NAME="(.*?)"'
        type_regex = r'label=(.*?) '
        code_regex = r'CODE="(.*?)" '        
        # lineNum_regex = r'LINE_NUMBER=(\d+) '
        # columnNum_regex = r'COLUMN_NUMBER=(\d+) '
        loc_regex = r'LINE_NUMBER=(\d+)' # LINE_NUMBER
        # childnum_regex = r'childNum:(\d+)' # TODO
        _id = re.findall(id_regex, chunk)
        # fid = re.findall(fid_regex, chunk)
        name = re.findall(name_regex, chunk)
        tp = re.findall(type_regex, chunk)
        code = re.findall(code_regex, chunk)
        loc = re.findall(loc_regex, chunk) 
        # childnum = re.findall(childnum_regex, chunk) # TODO

        if tp != []:
            if tp[0] in NODE_TYPE_LIST:
                node['type'] = NODE_TYPE_LIST[tp[0]]
                # if node['type']=='RETURNTYPE':
                #     continue
            else:
                print('unknown node type: ', tp[0])
                # print(chunk)
                node['type'] = 'UNKNOWN'


            node['ID'] = _id[0]
            # node['name'] = ' '.join(tokenizer(name[0])) if name else ''
            node['name'] = name[0] if name else ''
            node['location'] = loc[0] if loc else '' # TODO
            # node['code'] = ' '.join(tokenizer(code[0])) if code else ''
            node['code'] = code[0] if code else ''

        nodes.append(node)
    
    for chunk in edge_chunks:
        # edge_regex = r'((\d+) \-\> (\d+) \[.*label\=(.+?)) '
        edge_regex = r'(\d+) -> (\d+) \[.*label=(.+?) (VARIABLE="(.*?)")?\]'
        edge_info = re.findall(edge_regex, chunk, re.S)
        assert edge_info, 'edge_info is empty'
        edge_info = edge_info[0]
        assert edge_info[1], 'edge_info is empty'
        edge_type = edge_info[2]
        if edge_type in ['REF']:
            edges.append({'front':edge_info[1],'rear':edge_info[0],'type':edge_info[2], 'variable':edge_info[-1]})
        else:
            edges.append({'front':edge_info[0],'rear':edge_info[1],'type':edge_info[2], 'variable':edge_info[-1]})
        
    return nodes, edges

def get_graph(nodes, edges, g_type):
	# call_graph: 'ARGUMENT', 'RECEIVER', 'CALL
    if g_type == 'ast':
        edge_type_list = ['AST', 'CALL']
    elif g_type == 'pdg':
        edge_type_list = ['REACHING_DEF', 'PDG', 'DDG', 'CDG', 'REF', 'CALL'] # , 'ARGUMENT', 'RECEIVER', 'DOMINATE'
    elif g_type == 'ddg': 
        edge_type_list = ['REACHING_DEF', 'DDG', 'REF', 'CALL'] # , 'ARGUMENT', 'RECEIVER'
    elif g_type == 'cdg':
        edge_type_list = ['CDG', 'CALL'] # , 'DOMINATE'
    elif g_type == 'cfg':
        edge_type_list = ['CFG', 'CALL']
    elif g_type == 'dfg': # TODO: cannot find the data flow edge
        edge_type_list = ['REACHING_DEF', 'DDG', 'REF', 'CALL']
        # return get_dfg_graph(nodes, edges)
    else:
        raise Exception("No such graph type: %s"%g_type)
    
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
        if node['ID'] in tmp_nodes:
            tgt_nodes.append(node)

    return tgt_nodes, tgt_edges


def get_dfg_graph(nodes, edges):
    ddg_nodes, ddg_edges = get_graph(nodes, edges, 'ddg')
    tgt_nodes_edges = {}
    tmp_nodes = {}
    for edge in ddg_edges:
        edge_type = edge['type']
        front = edge['front']
        rear = edge['rear']
        if edge_type == 'REACHING_DEF':
            variable = edge['variable'] if 'variable' in edge else ''
        elif edge_type == 'DDG':
            variable = 'DDG'
        else:
            print('unknown edge type:', edge_type)
            continue
        
        if variable not in tgt_nodes_edges:
            tgt_nodes_edges[variable] = {'nodes':[], 'edges':[]}
            tmp_nodes[variable] = set()
        
        tgt_nodes_edges[variable]['edges'].append(edge)
        tmp_nodes[variable].update([front, rear])

    for node in ddg_nodes:
        for variable in tmp_nodes:
            if node['ID'] in tmp_nodes[variable]:
                tgt_nodes_edges[variable]['nodes'].append(node)

    return tgt_nodes_edges


def get_callee(nodes):
	callees = {}
	for node in nodes:
		code = node['code']
		name = node['name']
		if node['type']=='CALL':
			if 'operator' not in name:
				callees[name] = node
	# callees = list(set(callees))
	# callees = [node['name'] for node in nodes if node['type'] == "CALLEE"]
	# print('callees:', callees)

	return callees

def get_pointers(nodes, edges):
    pointers = []

    identifiers = []
    for node in nodes:
        node_code = node['code']
        node_name = node['name']
        if 'NULL' in node_code: 
            continue
        if node['type'] == 'IDEN' and node_name:
            identifiers.append(node_name)
        if node['type'] == 'CALL' and node_name:
            if 'operator' not in node_name:
                identifiers.append(node_name.strip('*'))
    # identifiers = [node['code'] for node in nodes if node['type'] == 'IDEN']
    identifiers = list(set(identifiers))
    
    tmp = [node for node in nodes if node['type'] == "IDENDECLSTATE" or node['type'] == "PARAM" or node['type'] == "CALL"]
    tmp_code_list = list(set([node['code'] for node in tmp]))
    # print(tmp_code_list)
	
    for node in tmp:
        code = node['code']
        code_split = node['code'].replace("*",' * ').split(' ')
        if code.find('=') != -1:
            code = code.split('=')[0]

        if code.find('*') != -1:
            # pointer = [i for i in identifiers if i in code]
            pointer = [i for i in identifiers if i in code_split]
            pointers.extend(pointer)
    pointers = list(set(pointers))
    # print(pointers)

    return pointers

def get_arrays(nodes, edges):
	arrays = []

	identifiers = [node['code'] for node in nodes if node['type'] == 'IDEN']
	tmp = [node for node in nodes if node['type'] == "IDENDECLSTATE" or node['type'] == "PARAM"]
	for node in tmp:
		code = node['code']
		name = node['name']
		if code.find(' = ') != -1:
			code = code.split(' = ')[0]

		if code.find('[') != -1:
			# array = [i for i in identifiers if i in code.split("[")[0]]
			array = [name] if name else []
			arrays.extend(array)
	arrays = list(set(arrays))
	# print("arrays:", arrays)

	return arrays

def get_operator_nodes(nodes, edges):
    operators = []

    expstmt_nodes = [node for node in nodes if node['type'] == "CALL"]
    # use <operator>.addition and <operator>.multiplication 
    # https://docs.joern.io/cpgql/calls/
    operator_name_list = ['<operator>.addition', '<operator>.multiplication']
    for exp in expstmt_nodes:
        # node_type = exp['type']
        # code = exp['code']
        name = exp['name']
        # if node_type=='CALL':
        if name in operator_name_list:
            operators.append(exp)
    print([i['code'] for i in operators])

    return operators


def get_forward_nodes(node, nodes, edges):
	forward_nodes_id = []
	node_id = node['ID']

	for edge in edges:
		if edge['front'] == node_id:
			forward_nodes_id.append(edge['rear'])

	forward_nodes = [node for node in nodes if node['ID'] in forward_nodes_id]
	return forward_nodes


def get_backward_nodes(node, nodes, edges):
	backward_nodes_id = []
	node_id = node['ID']

	for edge in edges:
		if edge['rear'] == node_id:
			backward_nodes_id.append(edge['front'])
			
	backward_nodes = [node for node in nodes if node['ID'] in backward_nodes_id]
	return backward_nodes


def forward_slice(criterion, nodes, edges):
	result = []
	visited = set()
	q = Queue.Queue()
	q.put(criterion)
	while not q.empty():
		current_node = q.get()
		result.append(current_node)
		forward_nodes_list = get_forward_nodes(current_node, nodes, edges)
		for forward_node in forward_nodes_list:
			if forward_node['ID'] not in visited:
				visited.add(forward_node['ID'])
				q.put(forward_node)
	return result


def backward_slice(criterion, nodes, edges):
	result = []
	visited = set()
	q = Queue.Queue()
	q.put(criterion)
	while not q.empty():
		u = q.get()
		result.append(u)
		g = get_backward_nodes(u, nodes, edges)
		for v in g:
			if v['ID'] not in visited:
				visited.add(v['ID'])
				q.put(v)
	return result
    

def bid_slice(criterion, nodes, edges):
	result = []
	rb = forward_slice(criterion, nodes, edges)
	rf = backward_slice(criterion, nodes, edges)
	for r in rb:
		if r not in result:
			result.append(r)
	for r in rf:
		if r not in result:
			result.append(r)
	return result


def construct_subgraph(_nodes, _edges):
	nodes = copy.deepcopy(_nodes)
	edges = copy.deepcopy(_edges)
	slice_nodes = []
	slice_edges = []
	slice_nodes_id = [slice_node['ID'] for slice_node in nodes]
	for edge in edges:
		if edge['front'] in slice_nodes_id and edge['rear'] in slice_nodes_id:
			slice_edges.append(edge)
			if nodes[slice_nodes_id.index(edge['front'])] not in slice_nodes:
				slice_nodes.append(nodes[slice_nodes_id.index(edge['front'])])
			if nodes[slice_nodes_id.index(edge['rear'])] not in slice_nodes:
				slice_nodes.append(nodes[slice_nodes_id.index(edge['rear'])])
	return slice_nodes, slice_edges