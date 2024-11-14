import sqlite3
from symbolic import dataDict
scale = '8k 16k 32k 64k'.split()
markdown = [0, 1]

conn = sqlite3.connect('symDataset/tasks/TableQA/dataset.sqlite')
cur = conn.cursor()

for dbn in dataDict.keys():
    cur.execute('SELECT * FROM {dbn} WHERE dbIdx<5 AND sampleIdx=1 AND questionIdx<14;'.format(dbn=dbn))
    rows = cur.fetchall()
    for r in rows:
        print(r)
        break
