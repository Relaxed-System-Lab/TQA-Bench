import os
import random
import simplejson as json
import pandas as pd
from urllib.request import urlretrieve

import sys
sys.path.append('.')
from workflow.tableFV import split2Choices
from benchmarkUtils.jsTool import JS

map = {
    'dirty': [
        'amazon-google',
        'dblp-acm',
        'dblp-googlescholar',
        'walmart-amazon'
    ],
    'structured': [
        'amazon-google',
        'dblp-acm',
        'dblp-googlescholar',
        'walmart-amazon'
    ],
    'textual': [
        'abt-buy',
        'amazon-google',
        'walmart-amazon'
    ]
}

parquetNames = ['gold.parquet', 'table_a.parquet', 'table_b.parquet']
dataPath = 'dataset/em'

def download():
    for k, v in map.items():
        for vi in v:
            comb = os.path.join('https://pages.cs.wisc.edu/~dpaulsen/sparkly_datasets/', k, vi)
            for pn in parquetNames:
                pnc = os.path.join(comb, pn)
                pnp = os.path.join(dataPath, k, vi)
                os.makedirs(pnp, exist_ok=True)
                urlretrieve(pnc, os.path.join(pnp, pn))
                print(pnp, 'finished!')

def rawPairGen():
    for tp, vs in map.items():
        for v in vs:
            pqp = os.path.join(dataPath, tp, v, parquetNames[0])
            gold = pd.read_parquet(pqp)
            pqp = os.path.join(dataPath, tp, v, parquetNames[1])
            table_a = pd.read_parquet(pqp)
            pqp = os.path.join(dataPath, tp, v, parquetNames[2])
            table_b = pd.read_parquet(pqp)
            pairsJS = os.path.join(dataPath, tp, v, 'pairs.json')
            saveList = []
            for _, row in gold.iterrows():
                id1 = row['id1']
                id2 = row['id2']
                aRow = table_a[table_a['_id'] == id1].iloc[0]
                bRow = table_b[table_b['_id'] == id2].iloc[0]
                adic = aRow.to_dict()
                bdic = bRow.to_dict()
                del adic['_id']
                del bdic['_id']
                saveList.append({
                    'id1': id1,
                    'id2': id2,
                    'row1': adic,
                    'row2': bdic
                })
            with open(pairsJS, 'w') as js:
                json.dump(saveList, js, indent=2, ignore_nan=True)

def processingPairs(pairs):
    idxPair = []
    row1List = {}
    row2List = {}

    for p in pairs:
        idxPair.append((p['id1'], p['id2']))
        row1List[p['id1']] = p['row1']
        row2List[p['id2']] = p['row2']

    idx1List = list(row1List.keys())
    idx2List = list(row2List.keys())

    truePair = []
    falsePair = []
    for i in range(0, len(idxPair), 4):
        # 四组一批, 前两个交换, 后两个直接添加
        pairSlice = idxPair[i:i+4]
        if len(pairSlice) != 4:
            break
        falseIdx = (pairSlice[0][0], pairSlice[1][1])
        if falseIdx not in idxPair:
            falsePair.append([row1List[falseIdx[0]], row2List[falseIdx[1]]])
        falseIdx = (pairSlice[1][0], pairSlice[0][1])
        if falseIdx not in idxPair:
            falsePair.append([row1List[falseIdx[0]], row2List[falseIdx[1]]])
        truePair.append([row1List[pairSlice[2][0]], row2List[pairSlice[2][1]]])
        truePair.append([row1List[pairSlice[3][0]], row2List[pairSlice[3][1]]])
    return truePair, falsePair

def emGen(bmSize=400):
    emRoot = 'dataset/task/em'
    os.makedirs(emRoot, exist_ok=True)
    jsPath = os.path.join(emRoot, 'task.json')
    truePairs = []
    falsePairs = []
    for tp, vs in map.items():
        for v in vs:
            pairsJS = os.path.join(dataPath, tp, v, 'pairs.json')
            pairs = JS(pairsJS).loadJS()
            tps, fps = processingPairs(pairs)
            truePairs.extend(tps)
            falsePairs.extend(fps)
    sampledTrue = random.sample(truePairs, bmSize * 2)
    sampledFalse = random.sample(falsePairs, bmSize * 2)
    choices = split2Choices(sampledTrue, sampledFalse, None)
    JS(jsPath).newJS(choices)

if __name__ == '__main__':
    # download()
    # rawPairGen()
    emGen()
