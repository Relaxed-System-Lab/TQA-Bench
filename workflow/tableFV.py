import os
from pprint import pprint
import pandas as pd

import sys

sys.path.append('.')
from benchmarkUtils.database import DB

def joinTables(dbp):
    db = DB(dbp)

    # 获取根表, 从这些表开始DFS遍历序的倒序就是join序
    rootKeys = db.getAllRootKeys()
    rootTables = [k for k, v in rootKeys.items() if len(v) == 0]
    # dfs的地图
    foreignKeys = db.getAllForeignKeys()
    tables = db.initDataFrame()

    def dfs(node, tables, foreignKeys)->pd.DataFrame:
        """
        使用dfs实现join操作
        """
        nodeFk = foreignKeys[node]
        if len(nodeFk) == 0:
            # 终止条件为叶节点
            return tables[node]
        tab = tables[node].copy()
        for item in nodeFk:
            currCol = item['currentColumn']
            forTab = item['foreignTable']
            forCol = item['foreignColumn']
            dfsTab = dfs(forTab, tables, foreignKeys)
            tab = pd.merge(tab, dfsTab, left_on=currCol, right_on=forCol)
        return tab

    fullTables = {}
    for tn in rootTables:
        try:
            fullTables[tn] = dfs(tn, tables, foreignKeys)
        except:
            pass

    return fullTables

def tableFVGen()

if __name__ == '__main__':
    scalePath = 'dataset/scaledDB/16k/'
    dbNames = os.listdir(scalePath)
    corr = 0
    for dbn in dbNames:
        dbp = os.path.join(scalePath, dbn, f'{dbn}.sqlite')
        ifJoinable = joinTables(dbp)
        if ifJoinable:
            corr += 1

    print(corr, len(dbNames))
