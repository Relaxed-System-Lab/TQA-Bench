import os
import time
import requests
import simplejson as json
from datetime import datetime


import sys

sys.path.append(".")
from symbolic import dataDict
from symDataloader.utils import TaskCore
from benchmarkUtils.LLM import gptCall
from benchmarkLoader import singlePrompt


def qaPrompt(dbStr, question, choices):
    totalQuestion = f"{dbStr}\n\n{question}\n\n{choices}"
    prompt = singlePrompt.format(question=totalQuestion)
    return prompt


def tool_call(
    prompt,
    proxies={
        "http": "socks5://127.0.0.1:7890",
        "https": "socks5://127.0.0.1:7890",
    },
):
    log_root = "symDataset/log/"
    os.makedirs(log_root, exist_ok=True)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    bodies = {
        "model": "gpt-5.1",
        "tools": [{"type": "code_interpreter", "container": {"type": "auto"}}],
        "instructions": "You are a personal math tutor. When asked a math question, write and run code using the python tool to answer the question.",
        "input": prompt,
    }
    msg = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        json=bodies,
        proxies=proxies,
    ).json()

    now_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    with open(os.path.join(log_root, f"{now_str}.json"), "w") as js:
        json.dump(msg, js, indent=2)
    # json.dump(msg, open("tmp-gpt-5-mini.json", "w"), indent=2)
    content = msg["output"][-1]["content"][0]["text"]
    return content


def gpt5ToolCall(dbStr, question, choices):
    prompt = qaPrompt(dbStr, question, choices)
    return tool_call(prompt)


def gpt5Call(dbStr, question, choices):
    prompt = qaPrompt(dbStr, question, choices)
    return gptCall("gpt-5.1", prompt, "tmp", "symDataset/results/TableQA/log")


if __name__ == "__main__":
    time.sleep(3600 * 2)
    dbRoot = "symDataset/scaledDB"  # path to extract symDataset.zip
    taskPath = "symDataset/tasks/TableQA/dataset.sqlite"  # TableQA's dataset.sqlite
    resultPath = "symDataset/results/TableQA/gpt_5-1-tool.sqlite"  # result sqlite
    tc = TaskCore(dbRoot, taskPath, resultPath)
    for k in dataDict.keys():
        for scale in ["8k", "16k", "32k", "64k"]:
            # for scale in ["16k"]:
            timeSleep = 0
            tc.testAll(
                "gpt-5.1",  # The model name saved in taskPath
                k,  # dataset
                scale,  # 8k, 16k, 32k, 64k, 128k
                True,  # if use markdown
                5,  # dbLimit, 10 is ok
                1,  # sampleLimit, 1 is ok
                14,  # questionLimit, 14 is ok
                # gpt5ToolCall,
                gpt5Call,
                timeSleep,
            )
