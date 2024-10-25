import re
import os
from tqdm import tqdm
from datetime import datetime
from uuid import uuid4

from benchmarkUtils.LLM import gptCall
from benchmarkUtils.jsTool import JS
from benchmarkLoader.tableQALoader import TableQADataset
from benchmarkLoader.tableFVLoader import TableFVDataset
from benchmarkLoader.retrievalLoader import RetrievalDataset
from benchmarkLoader.cpaLoader import CPADataset
from benchmarkLoader.ctaLoader import CTADataset
from benchmarkLoader.emLoader import EMDataset

dsDict = {
    'qa': TableQADataset,
    'fv': TableFVDataset,
    'ret': RetrievalDataset,
    'cpa': CPADataset,
    'cta': CTADataset,
    'em': EMDataset
}

def extractAnswer(text:str)->str:
    patt = r'answer:\s*([A-F]+)'
    grps = re.findall(patt, text, re.IGNORECASE)
    if grps:
        return grps[-1].upper()
    return ''

def evalFile(filePath):
    saveList = JS(filePath).loadJS()
    cnt = sum([1 for item in saveList if item['right']])
    err = sum([1 for item in saveList if item['error'] is not None])
    tot = len(saveList)
    print('right choices', cnt)
    print('call errors', err)
    print('total', tot)
    print('acc (ignore call errors)', cnt / (tot - err))
    print('acc', cnt / tot)

def evalAcc(ds, # dataset type above
            scale, # 8k-128k (not suitable for em)
            markdown, # True or False (not suitable for em)
            model, # gpt-4, gpt-4o, gpt-4o-mini
            logRoot, # logRoot
            resultPath # result json path
            ):
    global dsDict
    if ds not in dsDict.keys():
        return None
    if logRoot == None:
        logRoot = os.path.join('results', ds)
    if resultPath == None:
        tmp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + "_" + str(uuid4()) + ".json"
        resultName = f'{ds}_{scale}_{markdown}_{model}_{tmp}'
        resultPath = os.path.join('results', resultName)


    dataset = None
    if ds == 'em':
        dataset = dsDict[ds]()
    else:
        dataset = dsDict[ds](scale, markdown)

    idx = 0
    saveList = []
    for q, c in tqdm(dataset, ds):
        pred = ''
        err = None
        try:
            res = gptCall(
                model,
                q,
                f'{ds}-{idx}',
                logRoot
            )
            pred = extractAnswer(res)
        except Exception as e:
            err = str(e)
        saveList.append({
            'idx': idx,
            'gt': c,
            'pred': pred,
            'right': c == pred,
            'error': err
        })
        JS(resultPath).newJS(saveList)
        idx += 1
        break

    evalFile(resultPath)


if __name__ == '__main__':
    for ds in dsDict.keys():
        evalAcc(
            ds,
            '16k',
            True,
            'gpt-4o-mini',
            None,
            None
        )
