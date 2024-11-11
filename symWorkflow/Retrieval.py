import os
import random

import sys
sys.path.append('.')
from benchmarkUtils.jsTool import JS
from symbolic import dataDict
from benchmarkUtils.database import DB

choicesMap = 'A B C D E F'.split()

def choicesGen(trueItems, falseItems):
    ti = [(item, True) for item in trueItems]
    fi = [(item, False) for item in falseItems]
    allItem = ti + fi[:4 - len(ti)]
    random.shuffle(allItem)
    rightIdx = []
    for idx in range(4):
        if allItem[idx][1]:
            rightIdx.append(idx)
    needOther = len(rightIdx) < len(ti)
    return [item[0] for item in allItem[:4]], rightIdx, needOther

def retrievalGen(dbRoot, dstRoot):
    global dataDict
    os.makedirs(dstRoot, exist_ok=True)
    dstPath = os.path.join(dstRoot, 'dataset.json')
    tableNames = []
    for k, v in dataDict.items():
        if k in ['food_facility_inspections', 'food_inspection']:
            continue
        dbp = os.path.join(dbRoot, '8k', k, '0.sqlite')
        db = DB(dbp)
        for tn in db.tables:
            tableNames.append((k, tn))

    idx = 0
    sz = len(tableNames)
    saveDict = {}
    for k, v in dataDict.items():
        saveDict[k] = []
        tab = v.retrieval
        questionIdx = 0
        for tableList in tab:
            trueItems = [(k, item) for item in tableList]
            falseItems = []
            while len(falseItems) < 3:
                if tableNames[idx] not in trueItems and tableNames[idx] not in falseItems:
                    falseItems.append(tableNames[idx])
                idx = (idx + 1) % sz
            choices, choiceIdx, needOther = choicesGen(trueItems, falseItems)
            saveDict[k].append({
                'questionIdx': questionIdx,
                'choices': choices,
                'rightIdx': choiceIdx,
                'needOther': needOther
            })
            questionIdx += 1
    JS(dstPath).newJS(saveDict)

if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB'
    dstRoot = 'symDataset/tasks/Retrieval'
    retrievalGen(dbRoot, dstRoot)
