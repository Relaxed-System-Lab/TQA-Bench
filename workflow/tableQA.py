import os
import re
import random
from uuid import uuid4
from tqdm import tqdm

import sys


sys.path.append('.')
from workflow import prompts, scaleRoot, qaRoot, refScale, scaledDict
from benchmarkUtils.database import DB
from benchmarkUtils.jsTool import JS
from benchmarkUtils.LLM import gptCall
from benchmarkUtils.codeRun import codeExec

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

def rawQAGen(
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
            'model': model,
            'dbName': dbn,
            'originalDBPath': dbp,
            'cacheDBPath': dbCachePath,
            'sampleSize': sampleSize
        }
        res = gptCall( model,
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

def testCode(code, dbPath):
    db = DB(dbPath)
    tables = db.initDataFrame().copy()
    res = None
    try:
        res = codeExec(code, tables)
    except:
        pass
    return res

def validPairs(rawRoot, validRoot):
    """
    判断代码的可执行性
    """
    global scaledDict
    jsNames = os.listdir(rawRoot)
    os.makedirs(validRoot, exist_ok=True)

    for jsn in jsNames:
        if not jsn.endswith('.json'):
            # 排除一些不是json文件的内容
            continue
        jsp = os.path.join(rawRoot, jsn)
        dstJSP = os.path.join(validRoot, jsn)
        qcPairs = JS(jsp).loadJS()

        validPairs = []
        for qc in qcPairs:
            code = qc['code']
            dbp = qc['info']['originalDBPath']
            dbn = dbp.split('/')[-1].split('.')[0]
            res = {}
            dropQC = False
            zeroCount = 0
            for sc in scaledDict.keys():
                scaledDBP = os.path.join(scaleRoot, sc, dbn, f'{dbn}.sqlite')
                res[sc] = testCode(code, scaledDBP)
                if str(res[sc]) in ['0', '0.0']:
                    zeroCount += 1
                if res[sc] is None or str(res[sc]) == 'nan':
                    dropQC = True
                    break
                else:
                    res[sc] = str(res[sc])
            if dropQC or zeroCount > 1:
                # 当存在None或者所有的结果都是0的情况下, 则不需要这些QC对了
                continue
            del qc['info']
            qc['database'] = dbn
            qc['answer']  = res
            if len(set(qc['answer'].values())) < 3:
                # 不足3个的去掉, 当有3个的时候, 选择unk
                continue
            validPairs.append(qc)

        print('validPair/totalPair', len(validPairs), len(qcPairs))
        JS(dstJSP).newJS(validPairs)

def finalQADataset(qaRoot, validRoot):
    """
    将validRoot中的内容最后打乱重排, 如果只有3个选项, 则添加一个D选项为, 上述选项都不对
    """
    global scaledDict
    jsNames = [item for item in os.listdir(validRoot) if item.endswith('.json')]
    dstPath = os.path.join(qaRoot, 'task.json')

    allScaledQA = []
    dedupChoices = []
    for jsn in jsNames:
        jsp = os.path.join(validRoot, jsn)
        lst = JS(jsp).loadJS()
        for item in lst:
            possibleChoices = item.get('choices', ['There is no right choice above.'])
            answer = item['answer']
            rightAnsSet = list(set(answer.values()))
            random.shuffle(rightAnsSet)
            allChoices = rightAnsSet + possibleChoices[:4 - len(rightAnsSet)]
            item['choices'] = allChoices
            item['rightIdx'] = {}
            for sc in answer.keys():
                item['rightIdx'][sc] = allChoices.index(answer[sc])
            del item['answer']
            # del item['code']
            sortedChoices = '|'.join(sorted(item['choices']))
            if sortedChoices in dedupChoices:
                continue
            else:
                dedupChoices.append(sortedChoices)
            allScaledQA.append(item)
    allScaledQA.sort(key=lambda x: x['database'])
    print('final remained QA Size:', len(allScaledQA))
    JS(dstPath).newJS(allScaledQA)

if __name__ == '__main__':
    refRoot = os.path.join(scaleRoot, refScale)
    # rawQAGen(
    #     refRoot,
    #     qaRoot,
    #     'gpt-4o'
    # )
    # msg = JS('dataset/task/tableQA/log/tableQA_07-10-2024-10-51-39_faf3809f-4249-4965-8e39-46f199947ff9.json').loadJS()['message']
    # qm, cm = extractPairs(msg)
    # print(qm, cm)
    rawRoot = os.path.join(qaRoot, 'raw')
    validRoot = os.path.join(qaRoot, 'valid')
    # validPairs(rawRoot, validRoot)
    finalQADataset(qaRoot, validRoot)
