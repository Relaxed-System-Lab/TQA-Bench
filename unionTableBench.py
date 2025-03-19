import os
import time
import sqlite3
import pandas as pd
from tqdm import tqdm
from benchmarkUtils.database import DB
from benchmarkLoader import singlePrompt
from benchmarkUtils.LLM import gptCall
from symDataloader.utils import TaskCore, extractAnswer
from symbolic.airline import Airline

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
            node = node.strip().replace(' ', '_').replace('-', '_').replace('\t', '_') # 注意给定的dataframe名字要把空格之类的换掉, 否则没法跑
            return tables[node]
        tab = tables[node].copy()
        for item in nodeFk:
            currCol = item['currentColumn']
            forTab = item['foreignTable']
            forCol = item['foreignColumn']
            dfsTab = dfs(forTab, tables, foreignKeys)
            tab = pd.merge(tab, dfsTab, left_on=currCol, right_on=forCol, suffixes=('', f'({forTab}.{forCol}->{currCol})'), how='left')
        return tab

    fullTables = {}
    for tn in rootTables:
        fullTables[tn] = dfs(tn, tables, foreignKeys)

    return fullTables

class SinleTaskCore(TaskCore):
    def __init__(self, dbRoot, taskPath, resultPath) -> None:
        super().__init__(dbRoot, taskPath, resultPath)

    def testAll(self, model, dbn, scale, markdown, dbLimit, sampleLimit, questionLimit, func, timeSleep=0):
        """
        func need to be a call function have 3 arguments -- dbStr, question, choicesStr
        """
        if dbn != 'airline':
            return None

        for dbIdx in tqdm(range(dbLimit)):
            for sampleIdx in range(sampleLimit):
                for questionIdx in range(questionLimit):
                    if self.resultCheck(dbn, model, scale, markdown, dbIdx, sampleIdx, questionIdx):
                        continue
                    item = self.loadTaskItem(dbn, scale, dbIdx, sampleIdx, questionIdx)
                    if item is None:
                        continue
                    dbp = os.path.join(self.dbRoot, scale, dbn, f'{dbIdx}.sqlite')
                    db = Airline(dbp)
                    if markdown:
                        dbStr = db.singleTables[questionIdx].to_markdown()
                    else:
                        dbStr = db.singleTables[questionIdx].to_csv()
                    choicesStr = TaskCore.generateChoices(item[-4:])
                    gt = TaskCore.getRightChoices(item[-5])
                    question = item[-6]

                    pred = ''
                    error = ''
                    res = ''
                    try:
                        res = func(dbStr, question, choicesStr)
                        pred = extractAnswer(res)
                        time.sleep(timeSleep)
                    except Exception as e:
                        print(e)
                        error = str(e)
                    self.resultCur.execute(TaskCore.inserttemplate.format(table_name=dbn),
                                            (model, scale, markdown, dbIdx, sampleIdx,
                                            questionIdx, gt, pred, gt==pred, error, res))
                    self.resultConn.commit()

def qaPrompt(dbStr, question, choices):
    totalQuestion = f'{dbStr}\n\n{question}\n\n{choices}'
    prompt = singlePrompt.format(question=totalQuestion)
    return prompt

def gpt4oCall(dbStr, question, choices):
    prompt = qaPrompt(dbStr, question, choices)
    return gptCall('gpt-4o-mini', prompt, 'tmp', 'symDataset/results/TableQA/log')

def resultAcc(dbp, cond=''):
    accStr = 'select sum(correct)*1.0/count(*) from airline;'
    countStr = 'select count(*) from airline;'
    if cond != '':
        accStr = f'select sum(correct)*1.0/count(*) from airline where {cond};'
        countStr = f'select count(*) from airline where {cond};'
    con = sqlite3.connect(dbp)
    cur = con.cursor()
    cur.execute(accStr)
    print(cur.fetchall())

    cur.execute(countStr)
    print(cur.fetchall())
    cur.close()
    con.close()

def compResult(singleDBP, multiDBP, model, dbLimit, sampleLimit, questionLimit):
    print(model)
    countCmd = f"select count(*) from airline where model='{model}' and scale='8k' and markdown=1 and dbidx<{dbLimit} and sampleidx<{sampleLimit} and questionidx<{questionLimit};"
    accCmd = f"select sum(correct) * 1.0 / count(*) from airline where model='{model}' and scale='8k' and markdown=1 and dbidx<{dbLimit} and sampleidx<{sampleLimit} and questionidx<{questionLimit};"
    singleCon = sqlite3.connect(singleDBP)
    multiCon = sqlite3.connect(multiDBP)
    res1 = singleCon.execute(countCmd).fetchall()
    res2 = singleCon.execute(accCmd).fetchall()
    print('single', res1[0][0], res2[0][0])
    res1 = multiCon.execute(countCmd).fetchall()
    res2 = multiCon.execute(accCmd).fetchall()
    print('multi', res1[0][0], res2[0][0])
    singleCon.close()
    multiCon.close()

if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB' # path to extract symDataset.zip
    taskPath = 'symDataset/tasks/TableQA/dataset.sqlite' # TableQA's dataset.sqlite
    resultPath = 'symDataset/results/TableQA/singleTask.sqlite' # result sqlite
    stc = SinleTaskCore(dbRoot, taskPath, resultPath)
    stc.testAll('gpt-4o-mini', 'airline', '8k', True, 10, 10, 14, gpt4oCall)
    # resultAcc(resultPath, "scale='8k' and markdown=1 and sampleIdx=0 and dbidx < 5")

    multiPath = 'tmp.sqlite' # result sqlite
    # model|scale|markdown|dbidx|sampleidx|questionidx|gt|pred|correct|error|message
    # compResult(resultPath, multiPath, 'gpt-4o-mini', 5, 1, 14)
    # compResult(resultPath, multiPath, 'gpt-4o', 5, 1, 14)
