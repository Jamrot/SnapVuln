# SnapVuln

# main.py
mode==1: test for D2A
1. 对每种类型漏洞使用submodel分别test
2. ensemble result

## def test(config)
-> ModelHandlerExtend.test

### ModelHandlerExtend.test
1. data_utils.read_all_Datasets

---
D2A-test (mode==1)

1. 设置 config['max_slices_num'] = 16
2. read_all_Datasets()读入test数据 "my_XX_test.jsonl.gz" ，每个instance为Graph类。
    - 在Graph类中，通过self.bulid_subgraph初始化。读入相应漏洞类型的slice（每个漏洞类型的slice会包含多个sample），随机选择config['max_slices_num']个sample，作为实际测试数据。如果sample数量小于config['max_slices_num']，则使用pad_subgraph填充，并标记为无效。
    - 其中，subgraph格式为list({'nodes': filter_code_nodes, 'edges': edges}, ...)
    - self.build_code_graph：对于nodes和edges进行处理，e.g., 转换为小写，如果没有name字段，使用code字段作为node_content，筛选指定名称的边。
3. DataStream()载入test数据，用于测试。

---
Joern-0.3.1

- 指定数据库位置
```
Next, specificy the location of the database created by joern in your Neo4J server configuration file in $Neo4jDir/conf/neo4j-server.properties:
# neo4j-server.properties
org.neo4j.server.database.location=/$path_to_index/.joernIndex/
```

