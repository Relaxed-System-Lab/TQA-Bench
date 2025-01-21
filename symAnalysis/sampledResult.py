import os
import sys
sys.path.append('.')

from benchmarkUtils.database import DB
from benchmarkUtils.LLM import countDBToken
from symbolic import dataDict

def cScience(val):
    rate = 0
    while val > 10:
        rate += 1
        val /= 10
    val = round(val, 2)
    return f'${val}\\times 10^{rate}$'.format(val=val, rate=rate)


if __name__ == '__main__':
    mean = lambda lst: str(cScience(sum(lst) / len(lst)))
    men = lambda lst: str(round(sum(lst) / len(lst), 2))
    totalRs = [.0, .0, .0, .0]
    totalTs = [.0, .0, .0, .0]
    for dbn in dataDict.keys():
        rs = []
        ts = []
        for sc in '8k 16k 32k 64k'.split():
            rows = []
            tokens = []
            for i in range(10):
                dbp = os.path.join('symDataset/scaledDB/', sc, dbn, f'{i}.sqlite')
                db = DB(dbp)
                for k, v in db.tables.items():
                    rows.append(len(v))
                tokens.append(countDBToken(dbp, True))
            rs.append(men(rows))
            ts.append(mean(tokens))
        # for i in range(4):
        #     totalRs[i] += float(rs[i])
        #     totalTs[i] += float(ts[i])
        print(dbn + ' & ' + ' & '.join(rs) + ' & ' + ' & '.join(ts) + ' \\\\')
    # print('total & ' + ' & '.join(['%.2f' % (it / 10) for it in totalRs]) + ' & ' + ' & '.join(['%.2f' % (it / 10) for it in totalTs]) + ' \\\\')
