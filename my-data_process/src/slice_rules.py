# - coding = utf-8-#
from slice_api import *

def bo_slice(nodes, edges):
	slices = []

	# get pointer, array and callee
	pointer_arrays = get_pointers(nodes, edges) + get_arrays(nodes, edges)
	callees = get_callee(nodes)
	if len(pointer_arrays) == 0 or len(callees) ==0:
		print("No pointer or arrays or callees.")
		return slices

	temp = []
	for node in nodes:
		if node['type'] == "CALL":
			for item in pointer_arrays:
				if item in node['code']:
					temp.append(node)
					break
	criterions = []
	for node in temp:
		for item in callees:
			if item in node['code']:
				criterions.append(node)
				break				
	pdg_nodes, pdg_edges = get_graph(nodes, edges, 'pdg')
	# print([i['code'] for i in criterions])
	# exit()
	for criterion in criterions:
		slice_nodes = backward_slice(criterion, pdg_nodes, pdg_edges)
		slice_nodes, slice_edges = construct_subgraph(slice_nodes, pdg_edges)
		if len(slice_edges) == 0 or len(slice_nodes) == 1:
			continue

		slice_content = {'criterion':criterion, 'nodes':slice_nodes,'edges':slice_edges}
		# slice_content['criterion'] = criterion
		slices.append(slice_content)
	return slices


def ml_slice(nodes, edges):
	slices = []

	pointer = get_pointers(nodes, edges)
	callees = get_callee(nodes)
	if len(pointer) == 0 or len(callees) ==0:
		print("No pointer or callees.")
		return slices

	temp = []
	for node in nodes:
		# if node['type'] == "CALL" and "=" in node['code']:
		if node['type'] == "CALL" and node['name']=='<operator>.assignment':
			for item in pointer:
				if item in node['code']:
					temp.append(node)
					break
	criterions = []
	for node in temp:
		for item in callees:
			if item in node['code']:
				criterions.append(callees[item])
				break	
	pdg_nodes, pdg_edges = get_graph(nodes, edges, 'pdg')
	for criterion in criterions:
		slice_nodes = forward_slice(criterion, pdg_nodes, pdg_edges)
		slice_nodes, slice_edges = construct_subgraph(slice_nodes, pdg_edges)
		if len(slice_edges) == 0 or len(slice_nodes) == 1:
			continue

		slice_content = {'criterion':criterion, 'nodes':slice_nodes,'edges':slice_edges}
		slices.append(slice_content)
	return slices


def io_slice(nodes, edges):
	slices = []

	criterions = get_operator_nodes(nodes, edges)
	if len(criterions) == 0:
		print("No operators.")
		return slices

	pdg_nodes, pdg_edges = get_graph(nodes, edges, 'pdg')
	for criterion in criterions:
		slice_nodes = bid_slice(criterion, pdg_nodes, pdg_edges)
		slice_nodes, slice_edges = construct_subgraph(slice_nodes, pdg_edges)
		if len(slice_edges) == 0 or len(slice_nodes) == 1:
			continue

		slice_content = {'criterion':criterion, 'nodes':slice_nodes,'edges':slice_edges}
		slices.append(slice_content)
	return slices


def np_slice(nodes, edges):
	slices = []

	def get_near_data_depend_node_location(ddg_nodes):
		location = [int(node['location']) for node in ddg_nodes if "location" in node.keys()]
		location = list(set(location))
		location.sort()		
		if len(location)>2:
			loc = location[2]
		elif len(location) >1:
			loc = location[1]
		else:
			loc = location[0]
		return loc

	pointer = get_pointers(nodes, edges)
	callees = get_callee(nodes)
	if len(pointer) == 0 or len(callees) ==0:
		print("No pointer or callees.")
		return slices

	temp = []
	for node in nodes:
		# if node['type'] == "CALL" and "=" in node['code']:
		if node['type'] == "CALL" and node['name']=='<operator>.assignment':
			for item in pointer:
				if item in node['code']:
					temp.append(node)
					break
	criterions = []
	for node in temp:
		for item in callees:
			if item in node['code']:
				# criterions.append(node)
				criterions.append(callees[item])
				break

	ddg_nodes, ddg_edges = get_graph(nodes, edges, 'ddg')
	cfg_nodes, cfg_edges = get_graph(nodes, edges, 'cfg')

	for criterion in criterions:
		ddg_slice_nodes = forward_slice(criterion, ddg_nodes, ddg_edges)
		if len(ddg_slice_nodes) == 1:
			print("No null pointer error. criterion: ", criterion['code'])
			continue
		near_location = get_near_data_depend_node_location(ddg_slice_nodes)

		cfg_slice_nodes = forward_slice(criterion, cfg_nodes, cfg_edges)
		slice_nodes = [node for node in cfg_slice_nodes if "location" in node.keys() and int(node['location']) < near_location+1]

		slice_nodes, slice_edges = construct_subgraph(slice_nodes, cfg_edges)
		if len(slice_edges) == 0 or len(slice_nodes) == 1:
			continue

		slice_content = {'criterion':criterion, 'nodes':slice_nodes,'edges':slice_edges}
		slices.append(slice_content)
	return slices


def uaf_slice(nodes, edges):
	slices = []

	pointers = get_pointers(nodes, edges)
	callees = get_callee(nodes)
	if len(pointers) == 0 or len(callees) ==0:
		print("No pointer or callees.")
		return slices

	node_with_pointer = []
	for node in nodes:
		code = node['code']
		code_split = code.split('=')[0].strip()
		# if node['type'] == "CALL" and "=" in node['code']:
		if node['type'] == "CALL" and node['name']=='<operator>.assignment':
			for pointer in pointers:
				# if pointer in node['code']:
				if pointer in code_split:
					node_with_pointer.append(node)
					break
	criterions = []
	for node in node_with_pointer:
		code = node['code']
		for callee in callees:
			if callee in code:
				# criterions.append(node)
				criterions.append(callees[callee])
				break			

	cfg_nodes, cfg_edges = get_graph(nodes, edges, 'cfg')
	for criterion in criterions:
		slice_nodes = forward_slice(criterion, cfg_nodes, cfg_edges)
		slice_nodes, slice_edges = construct_subgraph(slice_nodes, cfg_edges)
		if len(slice_edges) == 0 or len(slice_nodes) == 1:
			continue

		slice_content = {'criterion':criterion, 'nodes':slice_nodes,'edges':slice_edges}
		slices.append(slice_content)
	return slices


def df_slice(nodes, edges):
	slices = []

	pointers = get_pointers(nodes, edges)
	callees = get_callee(nodes)
	if len(pointers) == 0 or len(callees) ==0:
		print("No pointer or callees.")
		return slices
	
	node_with_pointer = []
	for node in nodes:
		code = node['code']
		regex_var = r'\s*\*?(\w+)\s*='
		var_find = re.findall(regex_var, code, re.S)
		code_split = var_find[0] if var_find else None
		# if node['type'] == "CALL" and "=" in node['code']: 
		if node['type'] == "CALL" and "=" in code and node['name']=='<operator>.assignment':
			for pointer in pointers:
				# if pointer in node['code']:
				if pointer==code_split:
					node_with_pointer.append({"pointer":pointer,"node":node})
					break

	criterions = []
	for item in node_with_pointer:
		node = item["node"]
		pointer = item["pointer"]
		for callee in callees:
			code = node['code']
			# if callee in node['code']:
			if callee in code:
				# criterions.append(callees[item])
				criterions.append({"pointer":pointer,"node":node})
				break		
	# for i in criterions:
	# 	print(i['code'])	

	dfg_nodes_edges_dict = get_graph(nodes, edges, 'dfg')
	for criterion_item in criterions:
		pointer = criterion_item["pointer"]
		criterion = criterion_item['node']
		if pointer not in dfg_nodes_edges_dict.keys():
			print("No data flow graph:", criterion['code'])
			continue
		dfg_nodes_edges = dfg_nodes_edges_dict[pointer]
		# dfg_nodes_edges.update(dfg_nodes_edges_dict['DDG'])
		dfg_nodes_edges_ddg = dfg_nodes_edges_dict['DDG']
		dfg_nodes_edges['nodes'].extend(dfg_nodes_edges_ddg['nodes'])
		dfg_nodes_edges['edges'].extend(dfg_nodes_edges_ddg['edges'])

		ddg_nodes, ddg_edges = dfg_nodes_edges['nodes'], dfg_nodes_edges['edges']
		slice_nodes = forward_slice(criterion, ddg_nodes, ddg_edges)
		slice_nodes, slice_edges = construct_subgraph(slice_nodes, ddg_edges)
		if len(slice_edges) == 0 or len(slice_nodes) == 1:
			print("no data flow:", criterion['code'])
			continue

		slice_content = {'criterion':criterion, 'nodes':slice_nodes,'edges':slice_edges}
		slices.append(slice_content)
	return slices