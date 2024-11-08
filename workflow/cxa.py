"""
For CPA and CTA task
"""

import os
import random
import pandas as pd
from tqdm import tqdm

import sys
sys.path.append('.')
from workflow import taskRoot, scaledDict
from benchmarkUtils.LLM import countDFToken
from benchmarkUtils.jsTool import JS

cpaPath = 'dataset/sotab-cpa'
ctaPath = 'dataset/sotab-cta'
labelXLSX = 'dataset/cxaLabels.xlsx'

def readLabels(labelXLSX):
    labelDF = pd.read_excel(labelXLSX)
    cls = labelDF['class'].tolist()
    cpaLabel = labelDF['CPA label'].tolist()
    cpaLabel = list(set(cpaLabel))
    labelDF['CTA label'][pd.notna(labelDF['fallback_CTA_label'])] = labelDF['fallback_CTA_label']
    ctaLabel = labelDF['CTA label'].tolist()
    ctaLabel = list(set(ctaLabel))
    return cpaLabel, ctaLabel


def loadDataset(cxaRoot):
    cxaRoot = cxaRoot[:-1] if cxaRoot.endswith('/') else cxaRoot
    cxa = cxaRoot[-3:]
    tableRoot = os.path.join(cxaRoot, 'Validation')
    labelPath = os.path.join(cxaRoot, cxa.upper() + '_validation_gt.csv')
    szPath = os.path.join(cxaRoot, 'size.json')
    scaledPath = os.path.join(cxaRoot, 'scale.json')
    csvNames = os.listdir(tableRoot)
    taskPath = os.path.join(taskRoot, cxa)
    os.makedirs(taskPath, exist_ok=True)

    tokenSize = {}
    if not os.path.isfile(szPath):
        for cn in tqdm(csvNames):
            cp = os.path.join(tableRoot, cn)
            df = pd.read_json(cp, compression='gzip', lines=True)
            sz = countDFToken(df, markdown=False)
            tokenSize[cn] = {
                'csv': sz,
                'md': -1
            }
            if sz <= 128 * 1024:
                tokenSize[cn]['md'] = countDFToken(df, markdown=True)
        JS(szPath).newJS(tokenSize)
    else:
        tokenSize = JS(szPath).loadJS()

    labels = pd.read_csv(labelPath)
    ls = list(set(labels['label'].tolist()))

    if not os.path.isfile(scaledPath):
        scaledCSV = {}
        for k in scaledDict.keys():
            scaledCSV[k] = []
        for k, v in tokenSize.items():
            mdSize = v['md']
            for sc, rg in scaledDict.items():
                if mdSize >= rg[0]*1024 and mdSize <= rg[1]*1024:
                    filtedLabels = labels[labels['table_name'] == k]
                    filtedData = filtedLabels.to_dict('split')['data']
                    scaledCSV[sc].extend(filtedData)
                    break
        JS(scaledPath).newJS(scaledCSV)
    else:
        scaledCSV = JS(scaledPath).loadJS()

    lp = 0
    for k, v in scaledCSV.items():
        scaledJS = os.path.join(taskPath, k)
        os.makedirs(scaledJS, exist_ok=True)

        taskList = []
        sampledData = random.sample(v, 400)
        for item in sampledData:
            print(item)
            csvName = item[0]
            columns = item[1:-1]
            lb = item[-1]
            lc = []
            while len(lc) < 3:
                if ls[lp] != lb:
                    lc.append(ls[lp])
                lp += 1
                lp %= len(ls)
            lc.append(lb)
            random.shuffle(lc)
            rightIdx = lc.index(lb)
            taskList.append({
                'table': csvName,
                'columns': columns,
                'choices': lc,
                'rightIdx': rightIdx
            })
        JS(os.path.join(scaledJS, 'task.json')).newJS(taskList)

if __name__ == '__main__':
    loadDataset(cpaPath)
    loadDataset(ctaPath)
#     readLabels(labelXLSX)
