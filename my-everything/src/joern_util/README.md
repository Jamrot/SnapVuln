1. 指定数据库位置

    ```
    vim /app/Tools-joern/neo4j/conf/neo4j-server.properties

    org.neo4j.server.database.location=/$path_to_index/.joernIndex/
    ```

2. 生成.joernIndex

    - 注意这里要输入dir path，而不是file path

    ```
    java -jar /app/Tools-joern/joern-0.3.1/bin/joern.jar [Code Dir]
    或
    java -Xmx16g -jar /app/Tools-joern/joern-0.3.1/bin/joern.jar [Code Dir]
    ```

3. 启动neo4j console

    ```
    /app/Tools-joern/neo4j/bin/neo4j console --db-path [/path/to/your/.joernIndex]
    ```