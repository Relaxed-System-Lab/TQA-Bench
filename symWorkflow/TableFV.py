import os
import sys
import sqlite3
import random

sys.path.append('.')
from symbolic import dataDict, symLoad, singleChoicePrompt, choiceMap, asmChoice
from symWorkflow.scaledSample import scaleDict
from benchmarkUtils.jsTool import JS
from benchmarkUtils.database import DB

createDatasetTemplate = """
CREATE TABLE IF NOT EXISTS {table_name} (
    scale TEXT,
    dbIdx INTEGER,
    sampleIdx INTEGER,
    questionIdx INTEGER,
    qtype TEXT,
    rightIdx INTEGER,
    A TEXT,
    B TEXT,
    C TEXT,
    D TEXT,
    PRIMARY KEY (scale, dbIdx, sampleIdx, questionIdx)
);
"""

primaryKeyCheck = """
SELECT 1
FROM {table_name}
WHERE scale = ? AND dbIdx = ? AND sampleIdx = ? AND questionIdx = ?;
"""

insertTemplate = """
INSERT OR IGNORE INTO {table_name}
(scale, dbIdx, sampleIdx, questionIdx, qtype, rightIdx, A, B, C, D)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

class TableFV:
    qtypes = 'row_match count average sum'.split()
    def __init__(self, dbRoot, taskRoot):
        self.dbRoot = dbRoot
        self.taskRoot = taskRoot
        os.makedirs(self.taskRoot, exist_ok=True)

        dataPath = os.path.join(self.taskRoot, 'dataset.sqlite')
        self.conn = sqlite3.connect(dataPath)
        self.cur = self.conn.cursor()

    @staticmethod
    def singleGen(dbn, dbp):
        dbClass = dataDict[dbn]
        rows = symLoad(dbClass, dbp)[:10]
        fvList = []
        for item in rows:
            if len(item) < 6:
                continue
            qtype, question, answer, rightIdx, choices, stmts = item[:6]
            trueStmts = [stmts[rightIdx]]
            stmts.pop(rightIdx)
            fvList.append({
                'qtype': qtype,
                'trueStmts': trueStmts,
                'falseStmts': stmts
            })
        return fvList

    @staticmethod
    def aggList(lst):
        qtypeAgg = {}
        for item in lst:
            if item['qtype'] not in qtypeAgg.keys():
                qtypeAgg[item['qtype']] = {
                    'trueStmts': [],
                    'falseStmts': []
                }
            qtypeAgg[item['qtype']]['trueStmts'].extend(item['trueStmts'])
            qtypeAgg[item['qtype']]['falseStmts'].extend(item['falseStmts'])

        for k, v in qtypeAgg.items():
            v['trueStmts'] = list(set(v['trueStmts']))
            v['falseStmts'] = list(set(v['falseStmts']))
        return qtypeAgg

    @staticmethod
    def splitTrueFalse(trueStmts, falseStmts):
        trueStmts = [(item, True) for item in trueStmts]
        falseStmts = [(item, False) for item in falseStmts]
        allStmts = trueStmts + falseStmts
        random.shuffle(allStmts)
        sz = len(allStmts)
        stmtPartition = []
        for i in range(0, sz, 4):
            stmtSlide = allStmts[i:i + 4]
            ts = [item[0] for item in stmtSlide if item[1] == True]
            fs = [item[0] for item in stmtSlide if item[1] == False]
            stmtPartition.append({
                'trueStmts': ts,
                'falseStmts': fs
            })
        return stmtPartition

    @staticmethod
    def shuffleChoice(trueStmts, falseStmts):
        trueStmts = [(item, True) for item in trueStmts]
        falseStmts = [(item, False) for item in falseStmts]
        allStmts = trueStmts + falseStmts
        random.shuffle(allStmts)
        rightIdxList = []
        for i in range(3, -1, -1):
            if allStmts[i][1]:
                rightIdxList.append(i)
        rightIdx = 0
        for n in rightIdxList:
            rightIdx = rightIdx * 10 + n
        allStmts = [item[0] for item in allStmts]
        if len(trueStmts) == 0:
            rightIdx = 4 # E choice
        return allStmts, rightIdx, rightIdxList

    def fvGen(self, n):
        for dbn in dataDict.keys():
            self.cur.execute(createDatasetTemplate.format(table_name=dbn))
            for scale in scaleDict.keys():
                scaledDBRoot = os.path.join(self.dbRoot, scale, dbn)
                dbNames = os.listdir(scaledDBRoot)
                for dbIdx in dbNames:
                    try:
                        idx = int(dbIdx.split('.')[0])
                    except:
                        continue
                    dbp = os.path.join(scaledDBRoot, dbIdx)
                    for sampleIdx in range(n):
                        allFVList = []
                        for _ in range(4):
                            fvList = TableFV.singleGen(dbn, dbp)
                            allFVList.extend(fvList)
                        aggedFVList = TableFV.aggList(allFVList)
                        saveList = []
                        for qtype in TableFV.qtypes:
                            splitDict = TableFV.splitTrueFalse(aggedFVList[qtype]['trueStmts'], aggedFVList[qtype]['falseStmts'])[:2] # only keep first
                            allStmts, rightIdx = TableFV.shuffleChoice(splitDict[0]['trueStmts'], splitDict[0]['falseStmts'])[:2]
                            saveList.append({
                                'qtype': qtype,
                                'choices': allStmts,
                                'rightIdx': rightIdx
                            })
                            allStmts, rightIdx = TableFV.shuffleChoice(splitDict[1]['trueStmts'], splitDict[1]['falseStmts'])[:2]
                            saveList.append({
                                'qtype': qtype,
                                'choices': allStmts,
                                'rightIdx': rightIdx
                            })
                        for questionIdx in range(len(saveList)):
                            self.cur.execute(insertTemplate.format(table_name=dbn),
                                             (scale, idx, sampleIdx, questionIdx,
                                              saveList[questionIdx]['qtype'],
                                              saveList[questionIdx]['rightIdx'],
                                              saveList[questionIdx]['choices'][0],
                                              saveList[questionIdx]['choices'][1],
                                              saveList[questionIdx]['choices'][2],
                                              saveList[questionIdx]['choices'][3]
                                              ))
                            self.conn.commit()


    @staticmethod
    def loadItem(datasetPath, dbRoot, dbn, scale, dbIdx, sampleIdx, questionIdx, markdown=True):
        conn = sqlite3.connect(datasetPath)
        cur = conn.cursor()
        cur.execute('SELECT * FROM {dbn} WHERE scale=? AND dbIdx=? AND sampleIdx=? AND questionIdx=?;'.format(dbn=dbn),
                    (scale, dbIdx, sampleIdx, questionIdx))
        item = cur.fetchone()
        dbp = os.path.join(dbRoot, scale, dbn, f'{dbIdx}.sqlite')
        if item:
            question = item[5]
            rightChoice = choiceMap[item[6]]
            choicesStr = asmChoice([item[7], item[8], item[9], item[10]])
            dbStr = DB(dbp).defaultSerialization(markdown)
            totalQuestion = f'# {dbn}\n\n{dbStr}\n\n{question}\n\n{choicesStr}'
            return singleChoicePrompt.format(question=totalQuestion), rightChoice
        return '', 'F'

if __name__ == '__main__':
    tqa = TableFV('symDataset/scaledDB', 'symDataset/tasks/TableFV')
    tqa.fvGen(10)
