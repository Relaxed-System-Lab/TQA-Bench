import os
from openai import OpenAI
import sqlite3
from symbolic import dataDict
from symDataloader.TableQADataset import qaPrompt
from benchmarkUtils.database import DB
from symDataloader.utils import TaskCore, extractAnswer
import simplejson as json

import sys

sys.path.append(".")


def genBatch(model, fileName):
    conn = sqlite3.connect("symDataset/tasks/TableQA/dataset.sqlite")
    cur = conn.cursor()
    # jslf = open('symDataset/tasks/TableQA/batch.jsonl')
    jslf = open(fileName, "w")

    for dbn in dataDict.keys():
        cur.execute(
            "SELECT * FROM {dbn} WHERE dbIdx<5 AND sampleIdx=0 AND questionIdx<14 AND scale in ('64k', '32k', '16k', '8k');".format(
                dbn=dbn
            )
        )
        rows = cur.fetchall()
        for r in rows:
            (
                scale,
                dbIdx,
                sampleIdx,
                questionIdx,
                qtype,
                question,
                rightIdx,
                A,
                B,
                C,
                D,
            ) = r
            choices = TaskCore.generateChoices([A, B, C, D])
            dbp = os.path.join("symDataset/scaledDB", scale, dbn, f"{dbIdx}.sqlite")
            db = DB(dbp)

            # insert markdown
            dbStr = db.defaultSerialization(True)
            prompt = qaPrompt(dbStr, question, choices)
            dic = {
                "custom_id": f"{1}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}-{rightIdx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                },
            }
            jslf.write(json.dumps(dic) + "\n")

            # insert csv
            # dbStr = db.defaultSerialization(False)
            # prompt = qaPrompt(dbStr, question, choices)
            # dic = {
            #     "custom_id": f"{0}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}-{rightIdx}",
            #     "method": "POST",
            #     "url": "/v1/chat/completions",
            #     "body": {
            #         "model": "gpt-4o",
            #         "messages": [
            #             {"role": "system", "content": "You are a helpful assistant."},
            #             {"role": "user", "content": prompt},
            #         ],
            #     },
            # }
            # jslf.write(json.dumps(dic) + "\n")

    jslf.close()


# file-SKLROSW6w5TKTdqPMyJBQxSI
def batchTest(filePath):
    print(filePath, "batch starting...")
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 百炼服务的base_url
    )
    batch_input_file = client.files.create(file=open(filePath, "rb"), purpose="batch")
    batch_input_file_id = batch_input_file.id
    print(batch_input_file_id)

    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "all questions."},
    )
    print(batch.id)


# batch_67373224f9f48190b9a145820c87006e
def statusCheck(batch_id):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 百炼服务的base_url
    )
    res = client.batches.retrieve(batch_id)
    err_content = client.files.content(res.error_file_id)
    err_content.write_to_file("tmp-error.jsonl")
    op_content = client.files.content(res.output_file_id)
    op_content.write_to_file("tmp-op.jsonl")


def stripInfo(text):
    # {1}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}-{rightIdx}
    _, dbn, scale, dbIdx, sampleIdx, questionIdx, rightIdx = text.split("-")
    return dbn, scale, dbIdx, sampleIdx, questionIdx, rightIdx


def resultWrite(jsonlFile, model, dstDBP):
    tc = TaskCore("", "./symDataset/tasks/TableQA/dataset.sqlite", dstDBP)
    markdown = True
    choices = "A B C D".split()
    error = ""
    with open(jsonlFile, "r") as jsl:
        for l in jsl:
            dic = json.loads(l)
            res = dic["response"]["body"]["choices"][0]["message"]["content"]
            pred = extractAnswer(res)
            lName = dic["custom_id"]
            dbn, scale, dbIdx, sampleIdx, questionIdx, rightIdx = stripInfo(lName)
            dbIdx = int(dbIdx)
            sampleIdx = int(sampleIdx)
            questionIdx = int(questionIdx)
            rightIdx = int(rightIdx)
            gt = choices[rightIdx]
            tc.resultCur.execute(
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
                    gt == pred,
                    error,
                    res,
                ),
            )
            tc.resultConn.commit()


def singleMultiGen(model, fileName, single=True):
    conn = sqlite3.connect("symDataset/tasks/TableQA/dataset.sqlite")
    cur = conn.cursor()
    jslf = open(fileName, "w")

    dbn = "airline"
    cur.execute(
        "SELECT * FROM {dbn} WHERE dbIdx<10 AND sampleIdx<10 AND questionIdx<14 AND scale in ('8k');".format(
            dbn=dbn
        )
    )
    rows = cur.fetchall()
    for r in rows:
        (
            scale,
            dbIdx,
            sampleIdx,
            questionIdx,
            qtype,
            question,
            rightIdx,
            A,
            B,
            C,
            D,
        ) = r
        choices = TaskCore.generateChoices([A, B, C, D])
        dbp = os.path.join("symDataset/scaledDB", scale, dbn, f"{dbIdx}.sqlite")

        if single:
            db = dataDict[dbn](dbp).singleTables[questionIdx]
            dbStr = db.to_markdown()
        else:
            db = DB(dbp)
            dbStr = db.defaultSerialization(True)

        prompt = qaPrompt(dbStr, question, choices)
        prefixIdx = 1 if single else 0
        dic = {
            "custom_id": f"{prefixIdx}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}-{rightIdx}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
            },
        }
        jslf.write(json.dumps(dic) + "\n")

    jslf.close()


def accTest(filePath):
    choices = "A B C D".split()
    accList = []
    with open(filePath, "r") as jsl:
        for l in jsl:
            dic = json.loads(l)
            res = dic["response"]["body"]["choices"][0]["message"]["content"]
            pred = extractAnswer(res)
            lName = dic["custom_id"]
            dbn, scale, dbIdx, sampleIdx, questionIdx, rightIdx = stripInfo(lName)

            rightIdx = int(rightIdx)
            gt = choices[rightIdx]
            accList.append(1 if gt == pred else 0)
    print(filePath, sum(accList) / len(accList))


if __name__ == "__main__":
    # model = "deepseek-r1"
    # filePath = f"tmp-{model}-multi-result.jsonl"
    # accTest(filePath)
    # filePath = f"tmp-{model}-single-result.jsonl"
    # accTest(filePath)
    # batchTest(filePath)
    resultWrite(
        "./tmp-deepseek-r1-multi-result.jsonl",
        "deepseek-r1",
        "./symDataset/results/TableQA/ds-r1-multi-result.sqlite",
    )
