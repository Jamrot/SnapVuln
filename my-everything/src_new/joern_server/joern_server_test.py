import requests
import json
import time
from cpgqls_client import CPGQLSClient, import_code_query, workspace_query

# 配置Joern服务器端点和认证信息
server_endpoint = "localhost:8081"
# basic_auth_credentials = ("username", "password")
# client = CPGQLSClient(server_endpoint, auth_credentials=basic_auth_credentials)
client = CPGQLSClient(server_endpoint)

# 执行一个简单的CPG查询
query = "val a = 1"
result = client.execute(query)
print("Simple query result:")
print(result)

# 执行`workspace` CPG查询
query = workspace_query()
result = client.execute(query)
print("Workspace query result:")
print(result['stdout'])

# 导入代码并生成CPG
code_path = "/app/slicing-snapvuln/my-everything/data/test_slice/response/a282a2f/code_new/net/ceph/messenger_v2.c"
project_name = "my-project"
query = import_code_query(code_path, project_name)
result = client.execute(query)
print("Import code query result:")
print(result['stdout'])

# 提交一个CPG查询
query = 'cpg.method.where(_.file.name).file.name.headOption'
result = client.execute(query)
print("CPG query result:")
print(result['stdout'])
