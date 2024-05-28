from joern.all import JoernSteps

j = JoernSteps()

j.setGraphDbURL('http://localhost:7474/db/data/')

# j.addStepsDir('my-simple')

j.connectToDatabase()

res =  j.runGremlinQuery("queryNodeIndex('type:Function')")

# res =  j.runCypherQuery('...')

# if not res:
    # print("None")

for r in res: 
    # print(r)
    query_str = """queryNodeIndex('functionId:%s AND isCFGNode:True').outE('REACHES')""" % (r)
    res_1 =  j.runGremlinQuery(query_str)
    # print(res_1)