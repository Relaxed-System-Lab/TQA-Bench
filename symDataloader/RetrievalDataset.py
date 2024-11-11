import os
import sqlite3
import time
from tqdm import tqdm

import sys
sys.path.append('.')
from symDataloader.utils import TaskCore, extractAnswer
from symbolic import dataDict
from benchmarkUtils.LLM import gptCall
from benchmarkUtils.jsTool import JS
from benchmarkUtils.database import DB
from benchmarkLoader import multiPrompt

choicesMap = 'A B C D E F'.split()
qaPath = 'symDataset/tasks/TableQA/dataset.sqlite'
retrievalPath = 'symDataset/tasks/Retrieval/dataset.json'
resultPath = 'symDataset/results/Retrieval/result.sqlite'
dbRoot = 'symDataset/scaledDB'

commonChoices = 'A) tableA\nB) tableB\nC) tableC\nD) tableD\nE) Still need other tables to get the answer.'
def loadDF(scale, dbIdx, dbTabList, markdown):
    dfStr = []
    idx = 0
    for dbn, tbn in dbTabList:
        dbp = os.path.join(dbRoot, scale, dbn, f'{dbIdx}.sqlite')
        db = DB(dbp)
        df = db.tables[tbn]
        if markdown:
            dfStr.append(f'## table{choicesMap[idx]}\n\n'+df.to_markdown())
        else:
            dfStr.append(f'## table{choicesMap[idx]}\n\n'+df.to_csv())
        idx += 1
    return '\n\n'.join(dfStr)

def retrievalTest(
    model,
    dbn,
    scale,
    markdown,
    dbLimit,
    sampleLimit,
    questionLimit,
    timeSleep
    ):
    resultRoot = os.path.dirname(resultPath)
    os.makedirs(resultRoot, exist_ok=True)
    qaConn = sqlite3.connect(qaPath)
    qaCur = qaConn.cursor()
    resultConn = sqlite3.connect(resultPath)
    resultCur = resultConn.cursor()

    retrievalItems = JS(retrievalPath).loadJS()[dbn]

    resultCur.execute(TaskCore.createresulttemplate.format(table_name=dbn))
    resultConn.commit()

    for dbIdx in tqdm(range(dbLimit)):
        for sampleIdx in range(sampleLimit):
            for questionIdx in range(questionLimit):
                dfStr = loadDF(scale, dbIdx, retrievalItems[questionIdx]['choices'], markdown)
                gt = ''.join(choicesMap[idx] for idx in retrievalItems[questionIdx]['rightIdx'])
                resultCur.execute(TaskCore.primarykeycheck.format(table_name=dbn), (model, scale, markdown, dbIdx, sampleIdx, questionIdx))
                if resultCur.fetchone():
                    continue
                qaCur.execute('SELECT question FROM {table_name} WHERE scale=? AND dbIdx=? AND sampleIdx=? AND questionIdx=?;'.format(table_name=dbn), (scale, dbIdx, sampleIdx, questionIdx))
                question = qaCur.fetchone()[0]
                totalQuestion = f'{dfStr}\n\nPlease select table(s) that can answer the following question\n{question}\n\n{commonChoices}'
                prompt = multiPrompt.format(question=totalQuestion)
                pred = ''
                error = ''
                res = ''
                try:
                    res = gptCall(model, prompt, 'retrieval', os.path.join(resultRoot, 'log'))
                    pred = extractAnswer(res)
                    time.sleep(timeSleep)
                except Exception as e:
                    error = str(e)
                resultCur.execute(TaskCore.inserttemplate.format(table_name=dbn),
                                        (model, scale, markdown, dbIdx, sampleIdx,
                                        questionIdx, gt, pred, gt==pred, error, res))
                resultConn.commit()
    resultConn.close()
    qaConn.close()

if __name__ == '__main__':
    retrievalTest(
        'gpt-4o-mini',
        'university',
        '8k',
        True,
        10,
        1,
        10,
        0
    )
