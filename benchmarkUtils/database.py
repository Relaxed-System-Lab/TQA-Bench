import os
import pandas as pd
import sqlite3
from tqdm import tqdm

class DB:
    def __init__(self, dbp, initTables=True):
        """
        这里要与旧版代码兼容, 因此添加了initTables用于初始化表格
        如果只是做采样, 建议设置为False以加快速度
        """
        self.dbp = dbp
        self.dbn = dbp.split('/')[-1].split('.')[0]

        self.conn = sqlite3.connect(self.dbp)
        # 牺牲一定的安全性大幅度提升性能
        self.conn.execute('PRAGMA journal_mode=WAL;')
        self.conn.commit()
        self.conn.execute('PRAGMA synchronous=OFF;')
        self.conn.commit()
        self.conn.execute('PRAGMA cache_size=-16777216') # 设置4GB缓存
        self.conn.commit()

        self.curs = self.conn.cursor()
        self.tableNames = []
        self.tableNames = self.getAllTableNames()

        self.tables = {}
        if initTables:
            self.tables = self.initDataFrame()

    def defaultSerialization(self, markdown=False):
        """
        markdown: True则序列化为markdown的表格, False则序列化为CSV格式
        默认的序列化方案, 可以选择是否使用markdown
        """
        tables = self.initDataFrame()

        tableList = []
        for k, v in tables.items():
            if markdown:
                tableList.append(f'## {k}\n\n{v.to_markdown(index=False)}')
            else:
                tableList.append(f'## {k}\n\n{v.to_csv(index=False)}')
        return '\n\n'.join(tableList)

    def rowCount(self, tabName):
        # 获取行数
        self.curs.execute(f'SELECT COUNT(*) FROM [{tabName}];')
        return self.curs.fetchall()[0][0]

    def schema(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        schema = cursor.fetchall()
        schemaList = [s[0] for s in schema]
        cursor.close()
        return '\n'.join(schemaList)
    
    def initDataFrame(self):
        if len(self.tables) > 0:
            return self.tables
        tablesName = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';", self.conn)

        dataframes = {}
        for tn in tablesName['name']:
            dataframes[tn] = pd.read_sql(f"SELECT * FROM [{tn}]", self.conn)
        self.tables = dataframes
        return dataframes
    
    def getAllTableNames(self):
        if len(self.tableNames) != 0:
            return self.tableNames
        # 获取所有的表格名
        self.curs.execute("""SELECT name 
                    FROM sqlite_master 
                    WHERE type = 'table' 
                    AND name NOT LIKE 'sqlite_%';
                """)
        res = self.curs.fetchall()
        tableNames = [item[0] for item in res]
        self.tableNames = tableNames
        return tableNames

    def getAllColumnNames(self, tbn):
        # 获取tbn所有的行名
        self.curs.execute(f"PRAGMA table_info([{tbn}]);")
        res = self.curs.fetchall()
        columnNames = [item[1] for item in res]
        return columnNames

    def getSingleForeignKey(self, tbn):
        # 获取tbn的外键信息
        self.curs.execute(f"PRAGMA foreign_key_list([{tbn}]);")
        res = self.curs.fetchall()
        foreignKey = []
        for item in res:
            foreignKey.append({'currentColumn': item[3], 'foreignTable': item[2], 'foreignColumn': item[4]})
        return foreignKey

    def getAllForeignKeys(self):
        # 这里获得的foreign key关系仅仅用于拓扑排序!
        tableNames = self.getAllTableNames()
        allForeignKeys = {}
        for tbn in tableNames:
            ret = self.getSingleForeignKey(tbn)
            allForeignKeys[tbn] = ret
        return allForeignKeys

    def getTableKey(self, tbn):
        self.curs.execute(f'PRAGMA table_info([{tbn}]);')
        res = self.curs.fetchall()
        k = []
        for item in res:
            if item[5] == 1:
                k.append(item[1])
        return k

    def getAllRootKeys(self):
        """
        在getALlForeignKeys中, 会返回一个dict, dict的key代表表格名tbn, value中的元素代表tbn中currentColumn与foreignTable中的foreignColumn相连接
        但在我们的实现中, 我们需要知道一个表格rootTable, 其rootColumn有哪些表格linkedTable的linkedColumn连进来了, 可能同一个column会有多个表连进来
        """
        allForeignKeys = self.getAllForeignKeys()
        allRootKeys = {}
        for k in allForeignKeys.keys():
            allRootKeys[k] = []
        for k, v in allForeignKeys.items():
            for item in v:
                # 注意, 有可能会省略
                allRootKeys[item['foreignTable']].append({'rootColumn': self.getTableKey(item['foreignTable'])[0] if item['foreignColumn'] is None else item['foreignColumn'],
                                                          'linkedTable': k,
                                                          'linkedColumn': item['currentColumn']})
        for k, v in allRootKeys.items():
            for item in v:
                for ik, iv in item.items():
                    if iv == None:
                        print(f'{ik} {iv}')
        return allRootKeys

    def getTopology(self):
        allForeignKeys = self.getAllForeignKeys()
        tableRely = {}
        for k, v in allForeignKeys.items():
            tableRely[k] = [item['foreignTable'] for item in v]

        topoOrder = []
        currTable = None
        while len(tableRely) > 0:
            currTable = None
            for k, v in tableRely.items():
                if len(v) == 0:
                    topoOrder.append(k)
                    currTable = k
                    break
            if currTable is None:
                print('There exists loop in this database.')
                return []
            for k, v in tableRely.items():
                while topoOrder[-1] in v:
                    v.remove(topoOrder[-1])
            del tableRely[currTable]
        return topoOrder

    def sample(self, dstPath, sampleNum=16, removeEmpty=True, removeOldVer=True):
        # 注意, 每次需要重新初始化cursor和connect, 刷新掉所有的临时表
        self.curs.close()
        self.conn.close()
        self.conn = sqlite3.connect(self.dbp)
        self.curs = self.conn.cursor()

        # 如果指定了要删除旧数据库, 且存在旧数据库, 则删除
        if removeOldVer and os.path.isfile(dstPath):
            os.remove(dstPath)
        topoOrder = self.getTopology()
        if len(topoOrder) == 0:
            return False

        allRootKeys = self.getAllRootKeys()

        # 新建一系列临时表, 这些表都是空表
        for tbn in topoOrder[::-1]:
            cmd = f"""
            CREATE TEMPORARY TABLE [Sampled{tbn}] AS SELECT * FROM [{tbn}] WHERE 1=0;
            """
            self.curs.execute(cmd)

        # 对表格进行采样, 使得表格满足外键关系
        for tbn in topoOrder[::-1]:
            if len(allRootKeys[tbn]) == 0:
                # 没有其他表格外键到tbn
                columnNames = self.getAllColumnNames(tbn)
                columnNames = [f'[{item}]' for item in columnNames] # 别忘了所有的column都要加上[]来防止有空格在里面

                cmd = f"""
                INSERT INTO [Sampled{tbn}]
                  WITH [Ordered{tbn}] AS (
                    SELECT *, ROW_NUMBER() OVER (ORDER BY ROWID) AS row_num
                    FROM [{tbn}]
                  )
                  SELECT {', '.join(columnNames)}
                  FROM [Ordered{tbn}]
                  WHERE row_num IN (
                    SELECT row_num
                    FROM [Ordered{tbn}]
                    ORDER BY RANDOM()
                    LIMIT {sampleNum}
                  )
                  ORDER BY row_num;
                """ # 这里创建的是一个临时表, 在本次连接中都有效, 创建VIEW会永久提交, 使用WITH只在当次查询中有效, 注意区分
                self.curs.execute(cmd)
            else:
                # 通过维护状态来实现复合外键关系, 但好像stmt的写法有问题
                artIdx = 0
                whereList = [allRootKeys[tbn][artIdx]]
                artIdx += 1
                while artIdx < len(allRootKeys[tbn]):
                    if whereList[-1]['linkedTable'] == allRootKeys[tbn][artIdx]:
                        whereList.append(allRootKeys[tbn][artIdx])
                    else:
                        if len(whereList) > 1:
                            print('There are more than 2 columns foreign key among 2 tables.')
                        whereStmt = ' AND '.join([f"[{tbn}].[{item['rootColumn']}] in (SELECT [Sampled{item['linkedTable']}].[{item['linkedColumn']}] FROM [Sampled{item['linkedTable']}])" for item in whereList])
                        cmd = f"""
                            INSERT INTO [Sampled{tbn}]
                              SELECT *
                              FROM [{tbn}]
                              WHERE {whereStmt};
                            """
                        self.curs.execute(cmd)
                        whereStmt = [allRootKeys[tbn][artIdx]]
                    artIdx += 1
                # 最后别忘了清空whereList中的剩余内容
                if len(whereList) > 1:
                    print('There are more than 2 columns foreign key among 2 tables.')
                whereStmt = ' AND '.join([f"[{tbn}].[{item['rootColumn']}] in (SELECT [Sampled{item['linkedTable']}].[{item['linkedColumn']}] FROM [Sampled{item['linkedTable']}])" for item in whereList])
                cmd = f"""
                  INSERT INTO [Sampled{tbn}]
                    SELECT *
                    FROM [{tbn}]
                    WHERE {whereStmt};
                  """
                self.curs.execute(cmd)

        # 将结果保存到另一个表中
        zeroRow = False
        newConn = sqlite3.connect(dstPath)
        newCurs = newConn.cursor()
        for tbn in topoOrder:
            self.curs.execute(f'SELECT sql FROM sqlite_master WHERE type="table" AND name="{tbn}";')
            createSQL = self.curs.fetchall()[0][0]
            newCurs.execute(createSQL)
            self.curs.execute(f'SELECT * FROM [Sampled{tbn}];')
            rows = self.curs.fetchall()
            if len(rows) > 0:
                qCount = len(rows[0])
                qStr = ', '.join(['?' for _ in range(qCount)])
                newCurs.executemany(f'INSERT OR IGNORE INTO [{tbn}] VALUES ({qStr})', rows)
            else:
                zeroRow = True
                print(f'Sampled {self.dbn} exists 0 row table {tbn}.')
        newConn.commit()
        newConn.close()

        if zeroRow and removeEmpty:
            os.remove(dstPath)

    def getMergedTable(self):
        """
        获取没有外键过来的表, 这些表用于与其他表内容join, 生成最后的大表
        这些大表后续会被采样row, 并prompt LLM生成text描述, 安插入fact-verification中, 作为简单样例
        """
        pass


if __name__ == '__main__':
    dbRoot = '/home/zipengqiu/TableDatasetGeneration/dataset/workflowDB/'
    dbNames = os.listdir(dbRoot)
#    dbNames = ['address']

    for dbn in tqdm(dbNames):
        dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
        db = DB(dbp)
        try:
            db.sample(f'dataset/{dbn}.sqlite', 1024)
        except Exception as E:
            print(E)
