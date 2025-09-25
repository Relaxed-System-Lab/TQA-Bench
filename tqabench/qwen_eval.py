import os
import requests
import simplejson as json
from datetime import datetime
from uuid import uuid4

from tqabench.utils.sqltest import TaskCore

from http import HTTPStatus
import dashscope


dataList = [
    "airline",
    "food_inspection",
    "movie",
    "music_tracker",
    "restaurant",
    "university",
    "cookbook",
    "food_facility_inspections",
    "water_quality",
    "global_biodiversity",
]

with open("tqabench/templates/sqlTemplate.txt", "r") as f:
    template = f.read()


def func(question, schema):
    prompt = template.format(
        question=f"# Database Schema\n\n{schema}\n\nQuestion: {question}"
    )
    response = dashscope.Generation.call(
        model="deepseek-r1",
        prompt=prompt,
        seed=1234,
        top_p=0.8,
        result_format="message",
        max_tokens=4096,
        temperature=0.85,
        repetition_penalty=1.0,
        request_timeout=300,
    )
    if response.status_code == HTTPStatus.OK:
        ctt = response["output"]["choices"][0]["message"]["content"]
        return ctt
    else:
        raise Exception(
            "Request id: %s, Status code: %s, error code: %s, error message: %s"
            % (
                response.request_id,
                response.status_code,
                response.code,
                response.message,
            )
        )


if __name__ == "__main__":
    dbRoot = "symDataset/scaledDB"  # path to extract symDataset.zip
    taskPath = "symDataset/tasks/TableQA/dataset.sqlite"  # TableQA's dataset.sqlite
    resultPath = "symDataset/results/TableQA/sql_qwen.sqlite"  # result sqlite
    tc = TaskCore(dbRoot, taskPath, resultPath)

    for k in dataList:
        for scale in ["8k", "16k", "32k", "64k"]:
            tc.testAll(
                "deepseek-r1",  # The model name saved in taskPath
                k,  # dataset
                scale,  # 8k, 16k, 32k, 64k, 128k
                5,  # dbLimit, 10 is ok
                1,  # sampleLimit, 1 is ok
                14,  # questionLimit, 14 is ok
                func,
            )
