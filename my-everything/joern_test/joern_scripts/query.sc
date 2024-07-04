// 查询源点（source）：a_real->struct_A_int[0] = 0;
val source = cpg.call.code("a_real->struct_A_int[0] = 0").l

// 查询汇点（sink）：c_real->struct_C_B.struct_B_A.struct_A_int[0]
val sink = cpg.call.code("c_real->struct_C_B.struct_B_A.struct_A_int[0]").l

// 查找从源到汇的数据流路径
val flows = sink.reachableByFlows(source)

// 打印结果
flows.p.foreach(println)
