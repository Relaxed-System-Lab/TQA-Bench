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

def gpt4oCall(dbStr, question, choices):
    prompt = qaPrompt(dbStr, question, choices)
    return gptCall('gpt-4o', prompt, 'tmp', 'symDataset/results/TableQA/log')

if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB' # path to extract symDataset.zip
    taskPath = 'symDataset/tasks/TableQA/dataset.sqlite' # TableQA's dataset.sqlite
    resultPath = 'symDataset/results/TableQA/4o.sqlite' # result sqlite
    tc = TaskCore(dbRoot, taskPath, resultPath)
    for k in dataDict.keys():
        for scale in ['8k', '16k', '32k', '64k']:
            timeSleep = 0
            if scale == '16k':
                timeSleep = 30
            elif scale == '32k':
                timeSleep = 60
            tc.testAll('gpt-4o', # The model name saved in taskPath
                    k, # dataset
                    scale, # 8k, 16k, 32k, 64k, 128k
                    False, # if use markdown
                    5, # dbLimit, 10 is ok
                    1, # sampleLimit, 1 is ok
                    14, # questionLimit, 14 is ok
                    gpt4oCall,
                    timeSleep)
            tc.testAll('gpt-4o', # The model name saved in taskPath
                    k, # dataset
                    scale, # 8k, 16k, 32k, 64k, 128k
                    True, # if use markdown
                    5, # dbLimit, 10 is ok
                    1, # sampleLimit, 1 is ok
                    14, # questionLimit, 14 is ok
                    gpt4oCall,
                    timeSleep)
