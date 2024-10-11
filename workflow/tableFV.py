import os
import re
import random
import pandas as pd
import simplejson as json
from tqdm import tqdm

import sys

sys.path.append('.')
from benchmarkUtils.LLM import gptCall
from workflow import prompts
from benchmarkUtils.database import DB
from benchmarkUtils.jsTool import JS

def DF2List(df):
    lst = []
    for _, v in df.iterrows():
        lst.append(v.to_dict())
    return lst

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
            fullTables[tn] = DF2List(dfs(tn, tables, foreignKeys))
        except:
            pass

    return fullTables

def extractQAStmt(text):
    patt = r'[A-E]\)\s*(.*)'
    grp = re.findall(patt, text)
    return grp

def QABasedGeneration(taskRoot):
    fvRoot = 'dataset/task/tableFV'
    logRoot = os.path.join(fvRoot, 'log')
    jsPath = os.path.join(fvRoot, 'QABased.json')
    choicesMap = 'A) B) C) D)'.split()
    taskList = JS(taskRoot).loadJS()
    template = prompts['fv_workflow']
    
    saveList = []
    if not os.path.isfile(jsPath):
        for t in tqdm(taskList):
            choices = t['choices']
            if 3 not in t['rightIdx'].values():
                # 去掉没有正确选项这一选项
                choices = choices[:3]
            answers = '\n'.join([f'{choicesMap[i]} {choices[i]}' for i in range(len(choices))])
            prompt = template.format(question=t['question'], answers=answers)
            res = gptCall('gpt-4o', prompt, 'QABased', logRoot)
            stmts = extractQAStmt(res)
            stmts = [s.strip() for s in stmts]
            if len(stmts) != len(choices):
                continue
            t['statements'] = stmts
            saveList.append(t)
            JS(jsPath).newJS(saveList)
    else:
        saveList = JS(jsPath).loadJS()

def extractStmt(text):
    patt = r'```txt\n(.*?)\n```'
    grp = re.findall(patt, text, re.DOTALL)
    if grp:
        return grp[0]
    return None

def rowBasedGeneration(dbRoot):
    dbNames = os.listdir(dbRoot)
    fvRoot = 'dataset/task/tableFV'
    logRoot = os.path.join(fvRoot, 'log')
    sampledRowsPath = os.path.join(fvRoot, 'sampledRows.json')
    stmtRowsPath = os.path.join(fvRoot, 'stmtRows.json')
    tfStmtRowsPath = os.path.join(fvRoot, 'tfStmtRows.json')
    os.makedirs(fvRoot, exist_ok=True)

    rows = {}
    if not os.path.isfile(sampledRowsPath):
        for dbn in dbNames:
            dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
            ftbs = joinTables(dbp)

            rows[dbn] = []
            for k, v in ftbs.items():
                if len(v) == 0:
                    continue
                rows[dbn].extend(v)
            # 按照信息数量从大到小排序
            rows[dbn].sort(key=lambda x: sum([1 for k, v in x.items() if str(v) not in ['None', 'nan']]), reverse=True)
            rows[dbn] = rows[dbn][:8]
        JS(sampledRowsPath).newJS(rows)
    else:
        rows = JS(sampledRowsPath).loadJS()

    template = prompts['multiExpEM_workflow']
    saveList = []
    if not os.path.isfile(stmtRowsPath):
        for k, v in tqdm(rows.items()):
            for dic in v:
                dicStr = json.dumps(dic, indent=2)
                prompt = template.replace('{row}', dicStr).replace('{database}', k)
                res = gptCall('gpt-4o', prompt, 'row2text', logRoot)
                stmt = extractStmt(res)
                saveList.append({
                    'database': k,
                    'row': dic,
                    'stmt': stmt
                })
                JS(stmtRowsPath).newJS(saveList)
    else:
        saveList = JS(stmtRowsPath).loadJS()

    tfStmtRows = []
    if not os.path.isfile(tfStmtRowsPath):
        for stmt in tqdm(saveList):
            if stmt['stmt'] is None:
                # 有时候是空, 这时候跳过就好
                continue

            # 对于非空的, 编写一个它的错误statement
            strKeys = [] # value是字符串的key, 且value在stmt里出现过
            for k, v in stmt['row'].items():
                if type(v) == str and v in stmt['stmt']:
                    strKeys.append(k)
            if len(strKeys) < 2:
                # 如果在stmt中不存在任何key, 说明都是数值/日期型, 这种不适合用作编写statement使用
                # 如果只有1个key, 说明替换这个key都会有潜在的正确风险, 因此不做
                continue

            # 读取数据库
            dbn = stmt['database']
            dbp = os.path.join('dataset/scaledDB/128k/', dbn, f'{dbn}.sqlite') # 注意, 这里要用128k的, 因为要保证false的在128k中也是错的
            tables = joinTables(dbp)
            for k in tables.keys():
                tables[k] = pd.DataFrame(tables[k])
            df = None
            for k, v in tables.items():
                colNames = v.columns.tolist()
                if set(colNames) == set(list(stmt['row'].keys())):
                    # 找到了相同的, 可以退出了
                    df = v
                    break

            if df is None:
                # 若没找到这样的df, 则退出 (正常情况都能找到)
                continue

            falseStmt = []
            for k in strKeys:
                col = df[k].tolist()
                col = [it for it in col if it != stmt['row'][k] and str(it) not in ['None', 'nan']]
                for c in col:
                    tmpDict = {}
                    for tk in strKeys:
                        if tk == k:
                            tmpDict[tk] = c
                        else:
                            tmpDict[tk] = stmt['row'][tk]
                    trueSeries = pd.Series(True, index=df.index)
                    for tk, tv in tmpDict.items():
                        trueSeries = trueSeries & (df[tk] == tv)
                    filtedRow = df[trueSeries]
                    if len(filtedRow) == 0:
                        falseStmt.append(stmt['stmt'].replace(stmt['row'][k], c))
            random.shuffle(falseStmt)
            stmt['falseStmt'] = falseStmt[:8]
            tfStmtRows.append(stmt)
            JS(tfStmtRowsPath).newJS(tfStmtRows)
    else:
        tfStmtRows = JS(tfStmtRowsPath).loadJS()
    return tfStmtRows

def QAGen(tfStmtRowsPath, QABasedPath):
    pass


if __name__ == '__main__':
    scalePath = 'dataset/scaledDB/16k/'
    # dbNames = os.listdir(scalePath)
    # corr = 0
    # for dbn in dbNames:
    #     dbp = os.path.join(scalePath, dbn, f'{dbn}.sqlite')
    #     ifJoinable = joinTables(dbp)
    #     if ifJoinable:
    #         corr += 1
    #
    # print(corr, len(dbNames))
    rowBasedGeneration(scalePath)
    taskRoot = 'dataset/task/tableQA/task.json'
    QABasedGeneration(taskRoot)
    QAGen('dataset/task/tableFV/tfStmtRows.json', 'dataset/task/tableFV/QABased.json')
