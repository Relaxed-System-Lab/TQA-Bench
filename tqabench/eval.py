import os
import requests
import simplejson as json
from datetime import datetime
from uuid import uuid4

from tqabench.utils.sqltest import TaskCore


def gptCall(
    model,
    prompt,
    logStart="",
    logPath="logs",
    proxies={
        "http": "socks5://127.0.0.1:7890",
        "https": "socks5://127.0.0.1:7890",
    },  # 代理字典, 这里默认使用1080端口的sock5代理
    OPENAI_API_KEY=None,
    otherInfo={},
    delPrompt=True,
):
    """
    model: gpt模型, 包括gpt-4, gpt-4o, gpt-4o-mini等
    prompt: 提示词
    logStart: 日志文件开头, 建议不要插入 `_` 在其中
    logPath: 日志文件地址, 若不存在则自动创建
    proxies: requests使用的代理地址, 默认是在1080端口的socks5代理
    OPENAI_API_KEY: openai的key, 如果保持None则读取环境变量
    """
    os.makedirs(logPath, exist_ok=True)
    if OPENAI_API_KEY is None:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    bodies = {
        "model": model,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }
    msg = None
    try:
        msg = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=bodies,
            proxies=proxies,
        ).json()
        # msg = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=bodies).json()
        msg = msg["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(str(msg))
    logInfo = {"model": model, "prompt": prompt, "message": msg}
    if delPrompt:
        del logInfo["prompt"]
    logInfo.update(otherInfo)
    fileName = (
        datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + "_" + str(uuid4()) + ".json"
    )
    if logStart != "":
        fileName = logStart + "_" + fileName
    filePath = os.path.join(logPath, fileName)
    with open(filePath, "w") as js:
        json.dump(logInfo, js, indent=2, ignore_nan=True)
    return msg


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

with open("tqabench/templates/arcticTemplate.txt", "r") as f:
    template = f.read()


def func(question, schema):
    prompt = template.format(question=question, schema=schema)
    return gptCall("gpt-4o-mini", prompt)


if __name__ == "__main__":
    dbRoot = "symDataset/scaledDB"  # path to extract symDataset.zip
    taskPath = "symDataset/tasks/TableQA/dataset.sqlite"  # TableQA's dataset.sqlite
    resultPath = "symDataset/results/TableQA/sql1.sqlite"  # result sqlite
    tc = TaskCore(dbRoot, taskPath, resultPath)

    for k in dataList:
        for scale in ["8k", "16k", "32k", "64k"]:
            tc.testAll(
                "gpt-4o-mini",  # The model name saved in taskPath
                k,  # dataset
                scale,  # 8k, 16k, 32k, 64k, 128k
                5,  # dbLimit, 10 is ok
                1,  # sampleLimit, 1 is ok
                14,  # questionLimit, 14 is ok
                func,
            )
