import random

import sys

sys.path.append('.')
from symbolic import dataDict
from symDataloader.utils import TaskCore
from benchmarkUtils.LLM import gptCall
from benchmarkLoader import singlePrompt

def qaPrompt(dbStr, question, choices):
    totalQuestion = f'{dbStr}\n\n{question}\n\n{choices}'
    prompt = singlePrompt.format(question=totalQuestion)
    return prompt

# -*- coding: utf-8 -*-
from http import HTTPStatus
import dashscope

def qwenCall(dbStr, question, choices):
    prompt = qaPrompt(dbStr, question, choices)
    response = dashscope.Generation.call(
        model='qwen2.5-72b-instruct',
        prompt=prompt,
        seed=1234,
        top_p=0.8,
        result_format='message',
        max_tokens=800,
        temperature=0.85,
        repetition_penalty=1.0,
        request_timeout=120
    )
    if response.status_code == HTTPStatus.OK:
        ctt = response['output']['choices'][0]['message']['content']
        print(ctt[:32])
        return ctt
    else:
        raise Exception('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))

# def gpt4oCall(dbStr, question, choices):
#     prompt = qaPrompt(dbStr, question, choices)
#     return gptCall('gpt-4o', prompt, 'tmp', 'symDataset/results/TableQA/log')

if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB' # path to extract symDataset.zip
    taskPath = 'symDataset/tasks/TableQA/dataset.sqlite' # TableQA's dataset.sqlite
    resultPath = 'symDataset/results/TableQA/qwen.sqlite' # result sqlite
    tc = TaskCore(dbRoot, taskPath, resultPath)
    for k in list(dataDict.keys()):
        for scale in ['64k']:
            timeSleep = 0
            tc.testAll('Qwen2.5-72B-Instruct', # The model name saved in taskPath
                    k, # dataset
                    scale, # 8k, 16k, 32k, 64k, 128k
                    True, # if use markdown
                    5, # dbLimit, 10 is ok
                    1, # sampleLimit, 1 is ok
                    14, # questionLimit, 14 is ok
                    qwenCall,
                    timeSleep)
