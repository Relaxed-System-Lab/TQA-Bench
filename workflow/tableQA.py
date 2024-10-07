import os
import re
from uuid import uuid4
from tqdm import tqdm

import sys


sys.path.append('.')
from benchmarkUtils.database import DB
from benchmarkUtils.jsTool import JS
from benchmarkUtils.LLM import gptCall

promptPath = 'workflow/templates.json'

prompts = JS(promptPath).loadJS()

def tableQAPrompt(dbPath, markdown=True):
    db = DB(dbPath)
    tables  = db.initDataFrame()
    
    # 获取拼接prompt的数据
    dfStmtList = []
    codeList = []
    sum_rows = 0
    for k, v in tables.items():
        dfStmtList.append(f'the table {k} is saved in DataFrame `{k}`')
        codeList.append(f'len({k})')
        sum_rows += len(v)

    prompt = prompts['qa_workflow'].format(
        datasetInfo=db.defaultSerialization(markdown=markdown),
        dfStmt=', '.join(dfStmtList),
        codeStr=' + '.join(codeList),
        sum_rows=str(sum_rows)
    )
    return prompt

def tableQAGen(
        dbRoot,
        qaRoot,
        model='gpt-4o-mini',
        sampleSize=4,
        markdown=True):

    # 初始化各个目录
    currUuid = str(uuid4())
    cacheRoot = os.path.join(qaRoot, 'cache', currUuid) # 缓存地址
    logRoot = os.path.join(qaRoot, 'log') # log地址
    rawRoot = os.path.join(qaRoot, 'raw') # js地址
    rawJSPath = os.path.join(rawRoot, f'{currUuid}.json')
    os.makedirs(cacheRoot, exist_ok=True)
    os.makedirs(logRoot, exist_ok=True)
    os.makedirs(rawRoot, exist_ok=True)

    dbNames = os.listdir(dbRoot)
    for dbn in tqdm(dbNames):
        dbp = os.path.join(dbRoot, dbn, f'{dbn}.sqlite')
        dbCachePath = os.path.join(cacheRoot, f'{dbn}.sqlite')
        DB(dbp).sample(dbCachePath, sampleSize, removeEmpty=False)
        prompt = tableQAPrompt(dbCachePath, markdown)
        otherInfo={
            'originalDBPath': dbp,
            'cacheDBPath': dbCachePath,
            'sampleSize': sampleSize
        }
        res = gptCall(
            model,
            prompt,
            'tableQA',
            logRoot,
            otherInfo=otherInfo
        )
        qm, cm = extractPairs(res)
        sz = len(qm)
        if sz != len(cm):
            print('Not Matched!')
            continue
        for i in range(sz):
            JS(rawJSPath).addJS({
                'question': qm[i],
                'code': cm[i],
                'info': otherInfo
            })

def extractPairs(text):
    qPat = r'question\s*\d*:\s*(.*)'
    qMatches = re.findall(qPat, text, re.IGNORECASE)
    cPat = r'```python\s*(.*?)\s*```'
    cMatches = re.findall(cPat, text, re.IGNORECASE|re.DOTALL)
    return qMatches, cMatches

if __name__ == '__main__':
    tableQAGen(
        'dataset/scaledDB/16k/',
        'dataset/task/tableQA/'
    )
    # msg = JS('dataset/task/tableQA/log/tableQA_07-10-2024-10-51-39_faf3809f-4249-4965-8e39-46f199947ff9.json').loadJS()['message']
    # qm, cm = extractPairs(msg)
    # print(qm, cm)
