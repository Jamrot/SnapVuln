import json 

content = """{"statements_slicing_strategy": [{ "statement_info": "<file_name> | <function_name> | <line>", "statement": "<code statement>", "slicing_direction": "<forward/backward/bidirectional>", "code_representation_graph": "<Control Flow Graph/Data Dependency Graph/Control Dependency Graph/Program Dependence Graph/Abstract Syntax Tree/Code Property Graph>", "justification": "<brief justification for your choices>" }, ... ]}"""

content_parse = json.dumps(content)

print(content_parse)