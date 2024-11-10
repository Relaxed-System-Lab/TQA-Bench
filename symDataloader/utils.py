import os
import re
import sqlite3
import time
from tqdm import tqdm

import sys
sys.path.append('.')
from benchmarkUtils.database import DB

def extractAnswer(text:str)->str:
    patt = r'answer:\s*([A-F]+)'
    grps = re.findall(patt, text, re.IGNORECASE)
    if grps:
        return grps[-1].upper()
    return ''

class TaskCore:
    choicesMap = 'A B C D E F'.split()
    createresulttemplate = """
    create table if not exists {table_name} (
        model text,
        scale text,
        markdown integer,
        dbidx integer,
        sampleidx integer,
        questionidx integer,
        gt text,
        pred text,
        correct integer,
        error text,
        message text,
        primary key (model, scale, markdown, dbidx, sampleidx, questionidx)
    );
    """

    primarykeycheck = """
    select 1
    from {table_name}
    where model = ? and scale = ? and markdown = ? and dbidx = ? and sampleidx = ? and questionidx = ?;
    """

    inserttemplate = """
    insert or ignore into {table_name}
    (model, scale, markdown, dbidx, sampleidx, questionidx, gt, pred, correct, error, message)
    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    def __init__(self, dbRoot, taskPath, resultPath) -> None:
        self.dbRoot = dbRoot
        self.taskPath = taskPath
        self.resultPath = resultPath
        dirPath = os.path.dirname(self.resultPath)
        os.makedirs(dirPath, exist_ok=True)

        self.taskConn = sqlite3.connect(self.taskPath)
        self.taskCur = self.taskConn.cursor()
        self.resultConn = sqlite3.connect(self.resultPath)
        self.resultCur = self.resultConn.cursor()

        self.tableNames = TaskCore.getAllTableNames(self.taskCur)

        for tn in self.tableNames:
            self.resultCur.execute(TaskCore.createresulttemplate.format(table_name=tn))
        self.resultConn.commit()

    def loadTaskItem(self, dbn, scale, dbIdx, sampleIdx, questionIdx):
        self.taskCur.execute('SELECT * FROM {dbn} WHERE scale=? AND dbIdx=? AND sampleIdx=? AND questionIdx=?;'.format(dbn=dbn),
                             (scale, dbIdx, sampleIdx, questionIdx))
        item = self.taskCur.fetchone()
        if item:
            return item
        return None

    @staticmethod
    def getAllTableNames(cursor:sqlite3.Cursor):
        cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name NOT LIKE \'sqlite_%\';')
        tableNames = []
        items = cursor.fetchall()
        if items:
            for it in items:
                tableNames.append(it[0])
        return tableNames

    @staticmethod
    def getTableColumns(cursor:sqlite3.Cursor, tbn:str):
        cursor.execute('SELECT * FROM {table_name} LIMIT 1;'.format(table_name=tbn))
        return [tup[0] for tup in cursor.description]

    @staticmethod
    def generateChoices(choicesList:list):
        choices = []
        for i in range(len(choicesList)):
            choices.append(f'{TaskCore.choicesMap[i]}) {choicesList[i]}')
        return '\n'.join(choices)

    @staticmethod
    def getRightChoices(rightIdx:int):
        rightChoices = []
        idxStr = str(rightIdx)
        for char in idxStr:
            val = int(char)
            rightChoices.append(TaskCore.choicesMap[val])
        rightChoices.sort()
        return ''.join(rightChoices)

    def resultCheck(self, dbn, model, scale, markdown, dbIdx, sampleIdx, questionIdx):
        """
        return: True means this index have already tested.
        """
        self.resultCur.execute(TaskCore.primarykeycheck.format(table_name=dbn),
                               (model, scale, markdown, dbIdx, sampleIdx, questionIdx))
        if self.resultCur.fetchone():
            return True
        return False

    def testAll(self, model, dbn, scale, markdown, dbLimit, sampleLimit, questionLimit, func, timeSleep=0):
        """
        func need to be a call function have 3 arguments -- dbStr, question, choicesStr
        """
        for dbIdx in tqdm(range(dbLimit)):
            for sampleIdx in range(sampleLimit):
                for questionIdx in range(questionLimit):
                    if self.resultCheck(dbn, model, scale, markdown, dbIdx, sampleIdx, questionIdx):
                        continue
                    item = self.loadTaskItem(dbn, scale, dbIdx, sampleIdx, questionIdx)
                    if item is None:
                        continue
                    dbp = os.path.join(self.dbRoot, scale, dbn, f'{dbIdx}.sqlite')
                    db = DB(dbp)
                    dbStr = f'#{dbn}\n\n{db.defaultSerialization(markdown)}'
                    choicesStr = TaskCore.generateChoices(item[-4:])
                    gt = TaskCore.getRightChoices(item[-5])
                    question = item[-6]

                    pred = ''
                    error = ''
                    res = ''
                    try:
                        res = func(dbStr, question, choicesStr)
                        pred = extractAnswer(res)
                        time.sleep(timeSleep)
                    except Exception as e:
                        error = str(e)
                    self.resultCur.execute(TaskCore.inserttemplate.format(table_name=dbn),
                                            (model, scale, markdown, dbIdx, sampleIdx,
                                            questionIdx, gt, pred, gt==pred, error, res))
                    self.resultConn.commit()
