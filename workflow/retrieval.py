import os
import random

import sys

sys.path.append('.')
from benchmarkUtils.jsTool import JS
from benchmarkUtils.database import DB
from benchmarkUtils.LLM import countDFToken

if __name__ == '__main__':
    qaPath = 'dataset/task/tableQA/task.json'
    scaleRoot = 'dataset/scaledDB/16k'
    taskList = JS(qaPath).loadJS()
    dbNames = os.listdir(scaleRoot)
    retrievalRoot = 'dataset/task/retrieval'
    os.makedirs(retrievalRoot, exist_ok=True)
    jsPath = os.path.join(retrievalRoot, 'task.json')

    saveList = []
    for t in taskList:
        dbn = t['database']
        dbp = os.path.join(scaleRoot, dbn, f'{dbn}.sqlite')
        db = DB(dbp)
        tables = db.initDataFrame()
        tableNames = list(tables.keys())
        validTableNames = [item for item in tableNames if item in t['code']]
        if len(tableNames) >= 4:
            # 只有当数据库本身表大于等于4个, 才能用作任务构建
            random.shuffle(tableNames)
            tableNames = tableNames[:4]
            rightIdx = [idx for idx in range(4) if tableNames[idx] in validTableNames]
            needOther = len(rightIdx) != len(validTableNames)
            saveList.append({
                'question': t['question'],
                'database': dbn,
                'choices': tableNames,
                'rightIdx': rightIdx,
                'needOther': needOther
            })
            JS(jsPath).newJS(saveList)
    print(len(saveList))
