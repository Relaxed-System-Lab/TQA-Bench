import os
import re
import ast
import sqlite3
import time
from tqdm import tqdm
import simplejson as json
import pandas as pd

from tqabench.utils.db import DB
from concurrent.futures import ThreadPoolExecutor


def list_check(l0, l1):
    if len(l0) != len(l1):
        return False
    for item in l0:
        if item not in l1:
            return False
    return True


def insertLine(file_path, text):
    with open(file_path, "a") as jsl:
        jsl.write(f"{text}\n")


def extract_sql(text):
    pattern = re.compile(r"<sql>(.*?)</sql>", re.DOTALL)
    results = pattern.findall(text)
    if results:
        return results[-1].strip()
    return ""


def extract_last_sql(text):
    pattern = re.compile(r"```sql\s*([\s\S]*?)```", re.IGNORECASE)
    matches = pattern.findall(text)
    if not matches:
        return ""
    return matches[-1].strip()


class TaskCore:
    choicesMap = "A B C D E F".split()
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
        self.taskCur.execute(
            "SELECT * FROM {dbn} WHERE scale=? AND dbIdx=? AND sampleIdx=? AND questionIdx=?;".format(
                dbn=dbn
            ),
            (scale, dbIdx, sampleIdx, questionIdx),
        )
        item = self.taskCur.fetchone()
        if item:
            return item
        return None

    @staticmethod
    def getAllTableNames(cursor: sqlite3.Cursor):
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        tableNames = []
        items = cursor.fetchall()
        if items:
            for it in items:
                tableNames.append(it[0])
        return tableNames

    @staticmethod
    def getTableColumns(cursor: sqlite3.Cursor, tbn: str):
        cursor.execute("SELECT * FROM {table_name} LIMIT 1;".format(table_name=tbn))
        return [tup[0] for tup in cursor.description]

    @staticmethod
    def generateChoices(choicesList: list):
        choices = []
        for i in range(len(choicesList)):
            choices.append(f"{TaskCore.choicesMap[i]}) {choicesList[i]}")
        return "\n".join(choices)

    @staticmethod
    def getRightChoices(rightIdx: int):
        rightChoices = []
        idxStr = str(rightIdx)
        for char in idxStr:
            val = int(char)
            rightChoices.append(TaskCore.choicesMap[val])
        rightChoices.sort()
        return "".join(rightChoices)

    def resultCheck(self, dbn, model, scale, markdown, dbIdx, sampleIdx, questionIdx):
        """
        return: True means this index have already tested.
        """
        self.resultCur.execute(
            TaskCore.primarykeycheck.format(table_name=dbn),
            (model, scale, markdown, dbIdx, sampleIdx, questionIdx),
        )
        if self.resultCur.fetchone():
            return True
        return False

    @staticmethod
    def tableLlamaSerialize(tbn: str, df: pd.DataFrame):
        cols = df.columns.to_list()
        colStr = "| " + " | ".join([str(it) for it in cols]) + " |"
        sz = len(df)
        rows = []
        for i in range(sz):
            row = df.iloc[i].to_list()
            row = [str(it) for it in row]
            rows.append("| " + " | ".join(row) + " |")
        rowsStr = " [SEP] ".join(rows)
        totalStr = f"[TLE] The table title is {tbn} . [TAB] {colStr} [SEP] {rowsStr}"
        return totalStr

    def dataGen(
        self,
        save_name,
        dbn,
        scale,
        dbLimit,
        sampleLimit,
        questionLimit,
        func,
    ):
        for dbIdx in tqdm(range(dbLimit)):
            for sampleIdx in range(sampleLimit):
                for questionIdx in range(questionLimit):
                    item = self.loadTaskItem(dbn, scale, dbIdx, sampleIdx, questionIdx)
                    dbp = os.path.join(self.dbRoot, scale, dbn, f"{dbIdx}.sqlite")
                    dbSchema = DB(dbp).schema()
                    question = item[-6]
                    prompt = func(question, dbSchema)
                    save_dict = {
                        "custom_id": f"{1}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}",
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": {
                            "model": "deepseek-r1",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are a helpful assistant.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                        },
                    }
                    insertLine(save_name, json.dumps(save_dict))

    def dataEval(
        self,
        save_name,
        dbn,
        scale,
        dbLimit,
        sampleLimit,
        questionLimit,
    ):
        markdown = 0
        data = {}
        with open(save_name, "r") as jsl:
            for line in jsl:
                item = json.loads(line)
                data[item["custom_id"]] = item

        for dbIdx in tqdm(range(dbLimit)):
            for sampleIdx in range(sampleLimit):
                for questionIdx in range(questionLimit):
                    item = self.loadTaskItem(dbn, scale, dbIdx, sampleIdx, questionIdx)
                    item_key = f"{1}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}"
                    model = None

                    # load
                    dbp = os.path.join(self.dbRoot, scale, dbn, f"{dbIdx}.sqlite")
                    gt = item[-4 + item[-5]]

                    res, pred, error = "", "", ""
                    try:
                        model = data[item_key]["response"]["body"]["model"]
                        res = data[item_key]["response"]["body"]["choices"][0][
                            "message"
                        ]["content"]
                    except Exception as e:
                        error = str(e)
                        print(error)
                    sql = extract_last_sql(res)
                    conn = sqlite3.connect(dbp)
                    cur = conn.cursor()
                    correct = 0
                    try:
                        cur.execute(sql)
                        fet = cur.fetchall()
                        pred = str(fet[0][0]) if fet else ""
                        if questionIdx in [1, 6]:
                            gt_list = ast.literal_eval(gt)
                            pred_list = [_item[0] for _item in fet]
                            if list_check(gt_list, pred_list):
                                correct = 1
                            pred = str(pred_list)
                        else:
                            correct = int(gt == pred)
                    except Exception as e:
                        error = str(e)
                    conn.close()
                    self.resultCur.execute(
                        TaskCore.inserttemplate.format(table_name=dbn),
                        (
                            model,
                            scale,
                            markdown,
                            dbIdx,
                            sampleIdx,
                            questionIdx,
                            gt,
                            pred,
                            correct,
                            error,
                            res,
                        ),
                    )
                    self.resultConn.commit()

    def testAll(
        self,
        model,
        dbn,
        scale,
        dbLimit,
        sampleLimit,
        questionLimit,
        func,
        max_workers=16,
    ):
        """
        func need to be a call function have 3 arguments -- dbStr, question, choicesStr
        """

        markdown = 0

        def run_single(item, dbIdx, sampleIdx, questionIdx):
            dbp = os.path.join(self.dbRoot, scale, dbn, f"{dbIdx}.sqlite")
            dbSchema = DB(dbp).schema()
            gt = item[-4 + item[-5]]
            question = item[-6]

            # LLM 调用 + SQL 执行
            res, pred, error = "", "", ""
            try:
                res = func(question, dbSchema)
            except Exception as e:
                error = str(e)
            sql = extract_last_sql(res)
            conn = sqlite3.connect(dbp)
            cur = conn.cursor()
            correct = 0
            try:
                cur.execute(sql)
                fet = cur.fetchall()
                pred = str(fet[0][0]) if fet else ""
                if questionIdx in [1, 6]:
                    gt_list = ast.literal_eval(gt)
                    pred_list = [_item[0] for _item in fet]
                    if list_check(gt_list, pred_list):
                        correct = 1
                    pred = str(pred_list)
                else:
                    correct = int(gt == pred)
            except Exception as e:
                error = str(e)
            conn.close()
            return (
                model,
                scale,
                markdown,
                dbIdx,
                sampleIdx,
                questionIdx,
                gt,
                pred,
                correct,
                error,
                res,
            )

        for dbIdx in tqdm(range(dbLimit)):
            for sampleIdx in range(sampleLimit):
                for questionIdx in range(questionLimit):
                    if self.resultCheck(
                        dbn, model, scale, markdown, dbIdx, sampleIdx, questionIdx
                    ):
                        continue
                    item = self.loadTaskItem(dbn, scale, dbIdx, sampleIdx, questionIdx)
                    if item is None:
                        continue
                    single_result = run_single(item, dbIdx, sampleIdx, questionIdx)
                    (
                        model,
                        scale,
                        markdown,
                        dbIdx,
                        sampleIdx,
                        questionIdx,
                        gt,
                        pred,
                        correct,
                        error,
                        res,
                    ) = single_result
                    self.resultCur.execute(
                        TaskCore.inserttemplate.format(table_name=dbn),
                        (
                            model,
                            scale,
                            markdown,
                            dbIdx,
                            sampleIdx,
                            questionIdx,
                            gt,
                            pred,
                            correct,
                            error,
                            res,
                        ),
                    )
                    self.resultConn.commit()
