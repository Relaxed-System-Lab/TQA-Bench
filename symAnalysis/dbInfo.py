import os
import sys

sys.path.append('.')

from benchmarkUtils.database import DB
from symbolic import dataDict

if __name__ == '__main__':
    totSz = 0
    totCol = 0
    totRow = 0
    for dbn in dataDict.keys():
        dbp = os.path.join('dataset/workflowDB', dbn, f'{dbn}.sqlite')
        if not os.path.isfile(dbp):
            dbp = os.path.join('additional', dbn, f'{dbn}.sqlite')
        db = DB(dbp)
        sz = len(db.tables)
        colCnt = 0
        rowCnt = 0
        for k, v in db.tables.items():
            colCnt += len(v.columns)
            rowCnt += len(v)
        print(' & '.join([dbn, str(sz), "{:.2f}".format(colCnt / sz), "{:.2f}".format(rowCnt / sz)]) + ' \\\\')
        totSz += sz
        totCol += colCnt
        totRow += rowCnt
    print('total', totSz / len(dataDict), totCol / totSz, totRow / totSz)
