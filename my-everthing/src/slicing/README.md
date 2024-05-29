
### data storage

data_root
-> commit_id
    -> code_file: file_code_old-{commit_id}_{criterion_linenum}.c
    -> meta_file: meta-{commit_id}_{criterion_linenum}.json
    -> graph_dir: file_code_old-{commit_id}_{criterion_linenum}.graph
        -> graph_type_dump_dir: graph_{graph_type}
        -> bin_file: file_code_old-{commit_id}_{criterion_linenum}.c.bin
        -> graph_type_graph: graph_{graph_type}-file_code_old-{commit_id}_{criterion_linenum}.c.dot


patch_analyzer
- patch -> patch information

criterion_extractor
- patch information -> criterion information (meta)

