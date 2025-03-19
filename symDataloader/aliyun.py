import sys
import simplejson as json

sys.path.append(".")
from symbolic import dataDict
from symDataloader.utils import TaskCore
from benchmarkUtils.LLM import gptCall
from benchmarkLoader import singlePrompt


def qaPrompt(dbStr, question, choices):
    totalQuestion = f"{dbStr}\n\n{question}\n\n{choices}"
    prompt = singlePrompt.format(question=totalQuestion)
    return prompt


# -*- coding: utf-8 -*-
from http import HTTPStatus
import dashscope


def alicall(modelName, dbStr, question, choices):
    prompt = qaPrompt(dbStr, question, choices)
    response = dashscope.Generation.call(
        model=modelName,
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
        print(ctt[:32])
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


def insertLine(model, text):
    with open(f"tmp-{model}.jsonl", "a") as jsl:
        jsl.write(f"{text}\n")


def aligencall(modelName, dbStr, question, choices, othervals):
    dbn, scale, dbIdx, sampleIdx, questionIdx, rightIdx = othervals
    prompt = qaPrompt(dbStr, question, choices)
    item = {
        "custom_id": f"{1}-{dbn}-{scale}-{dbIdx}-{sampleIdx}-{questionIdx}-{rightIdx}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": modelName,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        },
    }
    itemStr = json.dumps(item)

    insertLine(modelName, itemStr)
    raise Exception("error")


def qwqPreviewCall(dbStr, question, choices, othervals):
    return aligencall("qwq-32b-preview", dbStr, question, choices, othervals)


def deepseekCall(dbStr, question, choices, othervals):
    return aligencall("deepseek-r1", dbStr, question, choices, othervals)


if __name__ == "__main__":
    dbRoot = "symDataset/scaledDB"  # path to extract symDataset.zip
    taskPath = "symDataset/tasks/TableQA/dataset.sqlite"  # TableQA's dataset.sqlite
    resultPath = "symDataset/results/TableQA/qwen_reasoning.sqlite"  # result sqlite
    tc = TaskCore(dbRoot, taskPath, resultPath)
    for scale in "8k 16k 32k 64k".split():
        print(scale)
        for k in list(dataDict.keys()):
            timeSleep = 0
            if scale != "64k":
                tc.testAll(
                    "qwq-32b-preview",  # The model name saved in taskPath
                    k,  # dataset
                    scale,  # 8k, 16k, 32k, 64k, 128k
                    True,  # if use markdown
                    5,  # dbLimit, 10 is ok
                    1,  # sampleLimit, 1 is ok
                    14,  # questionLimit, 14 is ok
                    qwqPreviewCall,
                    timeSleep,
                )
            tc.testAll(
                "deepseek-r1",  # The model name saved in taskPath
                k,  # dataset
                scale,  # 8k, 16k, 32k, 64k, 128k
                True,  # if use markdown
                5,  # dbLimit, 10 is ok
                1,  # sampleLimit, 1 is ok
                14,  # questionLimit, 14 is ok
                deepseekCall,
                timeSleep,
            )
