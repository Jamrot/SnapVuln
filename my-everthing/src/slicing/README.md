
### data storage

data_root
-> commit_id
    -> code_file: file_code_old-{commit_id}_{criterion_linenum}.c
    -> meta_file: meta-{commit_id}_{criterion_linenum}.json
    -> graph_dir: file_code_old-{commit_id}_{criterion_linenum}.graph
        -> graph_type_dump_dir: graph_{graph_type}
        -> bin_file: file_code_old-{commit_id}_{criterion_linenum}.c.bin
        -> graph_type_graph: graph_{graph_type}-file_code_old-{commit_id}_{criterion_linenum}.c.dot


## File Function Descriptions

patch_analyzer.py

    Function: Analyzes code patches.
    Main Content: Functions to analyze differences and changes in code patches.

build_graph_from_file_code.py

    Function: Builds a graph from file code.
    Main Content: Functions to parse file code and construct graph structures.

chatgpt_request.py

    Function: Handles requests to ChatGPT.
    Main Content: Functions to send and process requests to the ChatGPT API.

config.py

    Function: Configuration settings for the project.
    Main Content: Constants and configuration parameters used across the project.

criterion_extractor.py

    Function: Extracts criteria from code.
    Main Content: Functions to identify and extract specific criteria from source code.

graph_builder.py

    Function: Builds graphs from extracted data.
    Main Content: Functions to construct graphs using the extracted criteria and other data.

log_config.py

    Function: Sets up logging configuration.
    Main Content: Functions to configure logging settings and handlers.

logging.yaml

    Function: Logging configuration file.
    Main Content: YAML formatted settings for logging behavior and output.

response_parser.py

    Function: Parses responses from external services.
    Main Content: Functions to interpret and handle responses from APIs or other services.

slice_from_patch.py

    Function: Generates code slices from patches.
    Main Content: Functions to create code slices based on patches and differences.

slicer.py

    Function: Handles slicing operations.
    Main Content: Core slicing logic and related utility functions.