import os
import simplejson as json
import pandas as pd
from urllib.request import urlretrieve

import sys
sys.path.append('.')
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
                saveList.append([adic, bdic])
            with open(pairsJS, 'w') as js:
                json.dump(saveList, js, indent=2, ignore_nan=True)

def emGen():
    for tp, vs in map.items():
        for v in vs:
            pairsJS = os.path.join(dataPath, tp, v, 'pairs.json')
            pairs = JS(pairsJS).loadJS()
            print(tp, v, len(pairs))

if __name__ == '__main__':
    # download()
    # rawPairGen()
    emGen()
