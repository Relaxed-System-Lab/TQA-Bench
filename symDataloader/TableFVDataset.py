import sys

sys.path.append('.')
from symDataloader.utils import TaskCore
from benchmarkUtils.LLM import gptCall
from benchmarkLoader import multiPrompt

def fvPrompt(dbStr, question, choices):
    totalQuestion = f'{dbStr}\n\nWhich of the following statement(s) is correct?\n\n{choices}\nE) There is no correct statement above.'
    prompt = multiPrompt.format(question=totalQuestion)
    return prompt

def gpt4ominiCall(dbStr, question, choices):
    prompt = fvPrompt(dbStr, question, choices)
    return gptCall('gpt-4o-mini', prompt, 'tmp', 'symDataset/results/TableFV/log')

if __name__ == '__main__':
    dbRoot = 'symDataset/scaledDB' # path to extract symDataset.zip
    taskPath = 'symDataset/tasks/TableFV/dataset.sqlite' # TableQA's dataset.sqlite
    resultPath = 'symDataset/results/TableFV/result.sqlite' # result sqlite
    tc = TaskCore(dbRoot, taskPath, resultPath)
    tc.testAll('gpt-4o-mini', # The model name saved in taskPath
               'university', # dataset
               '8k', # 8k, 16k, 32k, 64k, 128k
               True, # if use markdown
               10, # dbLimit, 10 is ok
               1, # sampleLimit, 1 is ok
               8, # questionLimit, 8 is ok
               gpt4ominiCall)
