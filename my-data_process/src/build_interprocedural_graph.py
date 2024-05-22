import os
from tqdm import tqdm
import glob
import os
import glob
from tqdm import tqdm
import multiprocessing as mp
from build_interprocedural_graph_api import * 


def construct_graph(func,dot_folder,out_folder):
    call_dots = glob.glob(os.path.join(dot_folder,func.replace(".c","")+"*.c.dot"))
    if  len(call_dots) == 0:
        print("No call dots.")
        return
    # try:
    names, ids, callees_ast, callees_pdg, callees_cfg, callees_ddg, callees_cdg = get_func_id(call_dots)
    call_graph_edges = get_call_edges(names, ids, callees_ast, callees_pdg, callees_cfg, callees_ddg, callees_cdg)
    # except Exception as e:
    # 	print("%s No call graphs. "%func)
    # 	return

    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    with open(os.path.join(out_folder,func.replace(".c",".dot")),'w') as fd:
        for i, dotfile in enumerate(call_dots):
            with open(dotfile, 'r') as f:
                content = f.read()
            if i != 0:
                content = content.strip().lstrip('digraph G {')
            content = content.rstrip().rstrip('}')
            fd.write(content)
        fd.write(call_graph_edges+'}')


def get_func_id(dotfiles):
	"""
	Get the function names, ids, callees in AST, PDG, CFG, DDG, CDG
	"""
	names = []
	ids = []
	callees_ast = []
	callees_pdg = []
	callees_cfg = []
	callees_ddg = []
	callees_cdg = []
	for dotfile in dotfiles:
		nodes, edges = get_nodes_and_edges(dotfile)
		for node in nodes:
			name = node['name'] if 'name' in node else ''
			if node['type'] == "METHOD": # Method node
				names.append(node['name']) # method names
				ids.append(node['ID']) # method ids
			if node['type'] == "CALL" and name and 'operator' not in name: # Callee node
				correspond_node_pdg = get_correspond_node(node, nodes, edges, 'pdg')
				correspond_node_cfg = get_correspond_node(node, nodes, edges, 'cfg')
				correspond_node_ddg = get_correspond_node(node, nodes, edges, 'ddg')
				correspond_node_cdg = get_correspond_node(node, nodes, edges, 'cdg')
				callees_ast.append(node)
				callees_pdg.append(correspond_node_pdg)
				callees_cfg.append(correspond_node_cfg)	
				callees_ddg.append(correspond_node_ddg)		
				callees_cdg.append(correspond_node_cdg)	
	return names, ids, callees_ast, callees_pdg, callees_cfg, callees_ddg, callees_cdg


def get_call_edges(names, ids, callees_ast, callees_pdg, callees_cfg, callees_ddg=[], callees_cdg=[]):
	call_graph_edges = ''

	for i, call in enumerate(callees_ast):
		# call_func = call['code'] if 'code' in call else ''
		call_func = call['name'] if 'name' in call else ''
		call_id = call['ID']
		if call_func in names:
			### Add AST edge ####
			start = call_id
			end = ids[names.index(call_func)]
			edge = '  %s -> %s [ label=AST ]'%(start, end)
			call_graph_edges = call_graph_edges + edge + '\n'

			### Add PDG edge ####
			if callees_pdg[i] != None:
				start = callees_pdg[i]['ID']
				edge = '  %s -> %s [ label=PDG ]'%(start, end)
				call_graph_edges = call_graph_edges + edge + '\n'
			if callees_ddg[i] != None:
				start = callees_ddg[i]['ID']
				edge = '  %s -> %s [ label=DDG ]'%(start, end)
				call_graph_edges = call_graph_edges + edge + '\n'
			if callees_cdg[i] != None:
				start = callees_cdg[i]['ID']
				edge = '  %s -> %s [ label=CDG ]'%(start, end)
				call_graph_edges = call_graph_edges + edge + '\n'

			### Add CFG edge ####
			if callees_cfg[i] != None:
				start = callees_cfg[i]['ID']
				edge = '  %s -> %s [ label=CFG ]'%(start, end)
				call_graph_edges = call_graph_edges + edge + '\n'			
				
	return call_graph_edges


if __name__=="__main__":
	# func_folder = ""
	# function_files = os.listdir(func_folder)
	# for func in function_files:
	# multi_func = 'openssl-ff59ce71b50dbd735a065cb2a832ad870593845f_1-auto_labeler-INTEGER_OVERFLOW_L5-multi_function.c'
	dataset = 'bo-test'
	multi_dot_folder = 'my-data_process/data_test/{}/dot/vuln/multi'.format(dataset)
	combine_out_folder = 'my-data_process/data_test/{}/dot/vuln/combine'.format(dataset)
	multi_func = "my-BUFFER_OVERFLOW-multi_function.c"
	
	construct_graph(multi_func, dot_folder = multi_dot_folder, out_folder = combine_out_folder)