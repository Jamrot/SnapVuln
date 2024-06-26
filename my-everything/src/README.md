
patch_analyzer.py
- PatchAnalyzer
    - get_version: return version before and after patch
    - get_file_path: return file path before and after patch
    - get_file_code: return file code before and after patch
    - get_func_name: return func cname before and after patch
    - get_func_code: return func code before and after patch
    - get_statement: return deleted and added statement

graph_builder.py
- GraphBuilder
    - build_cpg
    - build_func_cpg
    - build_file_cpg
    - build_cross_file_cpg
    
- GraphParser
    - read_graph
    - get_nodes_and_edges


slicer.py
- Slicer
    - parse_stmt2criterion
    - get_graph
    - build_slice
    - forward_slicing
    - backword_slicing
    - bidirection_slicing


