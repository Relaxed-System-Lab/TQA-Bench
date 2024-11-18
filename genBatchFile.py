import os
from openai import OpenAI
import sqlite3
from symbolic import dataDict
from symDataloader.TableQADataset import qaPrompt
from benchmarkUtils.database import DB
from symDataloader.utils import TaskCore
import simplejson as json


def genBatch():
    conn = sqlite3.connect('symDataset/tasks/TableQA/dataset.sqlite')
    cur = conn.cursor()
    # jslf = open('symDataset/tasks/TableQA/batch.jsonl')
    jslf = open('tmp.jsonl', 'w')

    for dbn in dataDict.keys():
        cur.execute("SELECT * FROM {dbn} WHERE dbIdx<5 AND sampleIdx=1 AND questionIdx<13 AND scale in ('64k');".format(dbn=dbn))
        rows = cur.fetchall()
        for r in rows:
            scale, dbIdx, sampleIdx, questionIdx, qtype, question, rightIdx, A, B, C, D = r
            choices = TaskCore.generateChoices([A, B, C, D])
            dbp = os.path.join('symDataset/scaledDB', scale, dbn, f'{dbIdx}.sqlite')
            db = DB(dbp)

            # insert markdown
            dbStr = db.defaultSerialization(True)
            prompt = qaPrompt(dbStr, question, choices)
            dic = {
                "custom_id": f"{1}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}-{rightIdx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages":
                    [{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}],
                }
            }
            jslf.write(json.dumps(dic) + '\n')

            # insert csv
            dbStr = db.defaultSerialization(False)
            prompt = qaPrompt(dbStr, question, choices)
            dic = {
                "custom_id": f"{0}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}-{rightIdx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages":
                    [{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}],
                }
            }
            jslf.write(json.dumps(dic) + '\n')

    jslf.close()

# file-SKLROSW6w5TKTdqPMyJBQxSI
def batchTest():
    client = OpenAI()
    batch_input_file = client.files.create(
        file=open("tmp.jsonl", "rb"),
        purpose="batch"
        )
    batch_input_file_id = batch_input_file.id
    print(batch_input_file_id)

    client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
        "description": "gpt-4o 64k first 13 questions."
        }
    )

# batch_67373224f9f48190b9a145820c87006e
def statusCheck(batch_id):
    client = OpenAI()
    res = client.batches.retrieve(batch_id)
    print(res)


if __name__ == '__main__':
    # batchTest()
    statusCheck('batch_67373224f9f48190b9a145820c87006e')
