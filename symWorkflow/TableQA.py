import os
import sys
import sqlite3

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
    question TEXT,
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
(scale, dbIdx, sampleIdx, questionIdx, qtype, question, rightIdx, A, B, C, D)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

class TableQA:
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
        qaList = []
        for item in rows:
            if len(item) < 5:
                continue
            qtype, question, answer, rightIdx, choices = item[:5]
            choices = [str(it) for it in choices] # 防止转换不了
            qaList.append({
                'qtype': qtype,
                'question': question,
                'rightIdx': rightIdx,
                'choices': choices
            })
        return qaList

    def qaGen(self, n):
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
                        qaList = TableQA.singleGen(dbn, dbp)
                        for questionIdx in range(10):
                            item = qaList[questionIdx]
                            self.cur.execute(primaryKeyCheck.format(table_name=dbn), (scale, idx, sampleIdx, questionIdx))
                            if self.cur.fetchone():
                                # 如果存在, 则无需插入
                                continue
                            self.cur.execute(insertTemplate.format(table_name=dbn),
                                             (scale, idx, sampleIdx, questionIdx,
                                              item['qtype'], item['question'], item['rightIdx'],
                                              item['choices'][0],
                                              item['choices'][1],
                                              item['choices'][2],
                                              item['choices'][3]))
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
    tqa = TableQA('symDataset/scaledDB', 'symDataset/tasks/TableQA')
    tqa.qaGen(10)
    # taskRoot = 'symDataset/tasks/TableQA'
    # dbp = os.path.join(taskRoot, 'dataset.sqlite')
    # conn = sqlite3.connect(dbp)
    # cur = conn.cursor()
    # jsNames = [item for item in os.listdir(taskRoot) if item.endswith('.json')]
    # for jsn in jsNames:
    #     jsp = os.path.join(taskRoot, jsn)
    #     dbn = jsn.split('.')[0]
    #     cur.execute(createDatasetTemplate.format(table_name=dbn))
    #     dic = JS(jsp).loadJS()
    #     for sc, data in dic.items():
    #         for dbIdx in range(10):
    #             for sampleIdx in range(10):
    #                 for questionIdx in range(10):
    #                     item = data[dbIdx][sampleIdx][questionIdx]
    #                     cur.execute(primaryKeyCheck.format(table_name=dbn), (sc, dbIdx, sampleIdx, questionIdx))
    #                     if cur.fetchall():
    #                         continue
    #                     cur.execute(insertTemplate.format(table_name=dbn), (sc, dbIdx, sampleIdx, questionIdx,
    #                                                                         item['qtype'], item['question'], item['rightIdx'],
    #                                                                         item['choices'][0],
    #                                                                         item['choices'][1],
    #                                                                         item['choices'][2],
    #                                                                         item['choices'][3]))
    #                     conn.commit()
    #
    # conn.close()
