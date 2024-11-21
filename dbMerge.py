import os
import sqlite3
import argparse
import pandas as pd

import sys
sys.path.append('.')
from symDataloader.utils import TaskCore

questionTypes = {
    'row_match': [0, 5],
    'item_select': [1, 6],
    'count': [2, 7],
    'average': [3, 8],
    'sum': [4, 9],
    'difference': [10, 11],
    'correlation': [12, 13]
}

class ResultAnalysis:
    tableNameQuery = "SELECT name FROM sqlite_master WHERE type='table';"
    allRowsQueryTemplate = "SELECT * FROM {tn} WHERE message<>'';"
    def __init__(self, dst):
        self.conn = sqlite3.connect(dst)
        self.cur = self.conn.cursor()

    def mergeTables(self, src):
        if os.path.isdir(src):
            dbNames = [item for item in os.listdir(src) if item.endswith('.sqlite')]
            for dbn in dbNames:
                dbp = os.path.join(src, dbn)
                self.mergeTables(dbp)
            return True
        conn = sqlite3.connect(src)
        cur = conn.cursor()
        cur.execute(ResultAnalysis.tableNameQuery)
        tableNames = cur.fetchall()
        if tableNames:
            tableNames = [item[0] for item in tableNames]
        else:
            return False
        for tn in tableNames:
            self.cur.execute(TaskCore.createresulttemplate.format(table_name=tn))
            cur.execute(ResultAnalysis.allRowsQueryTemplate.format(tn=tn))
            rows = cur.fetchall()
            self.cur.executemany(TaskCore.inserttemplate.format(table_name=tn), rows)
            self.conn.commit()
        return True

    @staticmethod
    def removeEmptyMessage(dbp):
        conn = sqlite3.connect(dbp)
        cur = conn.cursor()
        cur.execute(ResultAnalysis.tableNameQuery)
        tableNames = cur.fetchall()
        if tableNames:
            tableNames = [item[0] for item in tableNames]
        else:
            return False
        for tn in tableNames:
            cur.execute("DELETE FROM {tn} WHERE message='';".format(tn=tn))
            conn.commit()
        return True

    def count(self, dbLimit, questionLimit):
        self.cur.execute(ResultAnalysis.tableNameQuery)
        tableNames = self.cur.fetchall()
        if tableNames:
            tableNames = [item[0] for item in tableNames]
        else:
            return False

        mergeInstructList = []
        for tn in tableNames:
            mergeInstructList.append("SELECT '{tn}', model, scale, markdown, dbIdx, sampleIdx, questionIdx, gt, pred, correct, error, message FROM {tn} WHERE message<>''".format(tn=tn))
        mergeInstruct = ' UNION ALL '.join(mergeInstructList)
        self.cur.execute("CREATE TEMP TABLE merged AS {mergeInstruct};".format(mergeInstruct=mergeInstruct))
        self.conn.commit()

        dfs = {}
        tab = pd.read_sql("SELECT markdown, model, scale, SUM(correct), COUNT(correct), SUM(correct) * 1.0 / COUNT(correct) \
        FROM merged WHERE message<>'' AND dbIdx<{dbLimit} AND sampleIdx=0 AND questionIdx<{questionLimit} GROUP BY model, scale, markdown ORDER BY markdown, model, CAST(REPLACE(scale, 'k', '') AS INTEGER);"
                         .format(dbLimit=dbLimit, questionLimit=questionLimit), self.conn)
        dfs['overview'] = tab

        for k, v in questionTypes.items():
            tab = pd.read_sql("SELECT markdown, model, scale, SUM(correct), COUNT(correct), SUM(correct) * 1.0 / COUNT(correct) \
            FROM merged WHERE message<>'' AND dbIdx<{dbLimit} AND sampleIdx=0 AND questionIdx<{questionLimit} AND questionIdx in ({qIdx}) GROUP BY model, scale, markdown ORDER BY markdown, model, CAST(REPLACE(scale, 'k', '') AS INTEGER);"
                             .format(dbLimit=dbLimit, questionLimit=questionLimit, qIdx=", ".join([str(it) for it in v])), self.conn)
            dfs[k] = tab

        return dfs

    def latexTableGen(self, dbLimit, questionLimit):
        dfs = self.count(dbLimit, questionLimit)
        for k, v in dbs.items():
            pass



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='To combine all result dataset together.')
    parser.add_argument('--dst', type=str, help='The destination sqlite to save all results.')
    parser.add_argument('--src', type=str, nargs='+', help='The list of result sqlite to combine.')
    args = parser.parse_args()
    if args.dst:
        ra = ResultAnalysis(args.dst)
        for src in args.src:
            ra.mergeTables(src)
    else:
        for src in args.src:
            ResultAnalysis.removeEmptyMessage(src)
    # cnt = ra.count(dbLimit=5, questionLimit=10)
    # print(cnt)
