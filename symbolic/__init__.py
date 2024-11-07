import os
import re
from uuid import uuid4
from tqdm import tqdm
from time import sleep
from pprint import pprint

import sys
sys.path.append('.')
from benchmarkUtils.LLM import gptCall
from benchmarkUtils.database import DB
from benchmarkUtils.dbSample import tokenBasedSample
from benchmarkUtils.jsTool import JS
from symbolic.airline import Airline
from symbolic.food_inspection import FoodInspection
from symbolic.movie import Movie
from symbolic.music_tracker import MusicTracker
from symbolic.restaurant import Restaurant
from symbolic.university import University

dataDict = {
    'airline': Airline,
    'food_inspection': FoodInspection,
    'movie': Movie,
    'music_tracker': MusicTracker,
    'restaurant': Restaurant,
    'university': University
}

choiceMap = 'A B C D E'.split()
with open('benchmarkLoader/prompts/singleChoicePrompt.txt', 'r') as txt:
    singleChoicePrompt = txt.read()
with open('benchmarkLoader/prompts/multiChoicePrompt.txt', 'r') as txt:
    multiChoicePrompt = txt.read()

def extractAnswer(text:str)->str:
    patt = r'answer:\s*([A-F]+)'
    grps = re.findall(patt, text, re.IGNORECASE)
    if grps:
        return grps[-1].upper()
    return ''

def acc(dstJs):
    lst = JS(dstJs).loadJS()
    error = 0
    total = 0
    correct = 0
    for item in lst:
        if item['error'] is not None:
            error += 1
        if item['gt'] == item['pred']:
            correct += 1
        total += 1
    return correct, error, total

def asmChoice(choices):
    choicesStr = []
    for i in range(min(5, len(choices))):
        choicesStr.append(f'{choiceMap[i]}) {choices[i]}')
    return '\n'.join(choicesStr)

def symLoad(symClass, dbp):
    sym = symClass(dbp)
    ret = []
    ret.append(('row_match',) + sym.q0())
    ret.append(('item_select',) + sym.q1())
    ret.append(('count',) + sym.q2())
    ret.append(('average',) + sym.q3())
    ret.append(('sum',) + sym.q4())
    ret.append(('row_match',) + sym.q5())
    ret.append(('item_select',) + sym.q6())
    ret.append(('count',) + sym.q7())
    ret.append(('average',) + sym.q8())
    ret.append(('sum',) + sym.q9())
    return ret

class BenchmarkDB:
    def __init__(self, dbRoot, dbn):
        self.dbn = dbn
        self.dbp = os.path.join(dbRoot, f'{dbn}.sqlite')
        self.taskRoot = os.path.join(dbRoot, 'task')
        self.resultRoot = os.path.join(dbRoot, 'result')
        self.logRoot = os.path.join(dbRoot, 'log')
        self.hashCode = str(uuid4())

        os.makedirs(self.taskRoot, exist_ok=True)
        os.makedirs(self.resultRoot, exist_ok=True)
        os.makedirs(self.logRoot, exist_ok=True)

        self.qaPath = os.path.join(self.taskRoot, f'TableQA_{self.hashCode}.json')
        self.qaResult = os.path.join(self.resultRoot, f'TableQA_{self.hashCode}.json')

    def qaGen(self):
        symRows = symLoad(dataDict[self.dbn], self.dbp)
        qaList = []
        for row in symRows:
            if len(row) < 5:
                continue
            qtype, question, answer, rightIdx, choices = row[:5]
            choices = [str(it) for it in choices]
            item = {
                'qtype': qtype,
                'question': question,
                'rightIdx': rightIdx,
                'choices': choices
            }
            qaList.append(item)
        if len(qaList) != 10:
            return False
        JS(self.qaPath).newJS(qaList)
        return True

    @staticmethod
    def formPrompt(item, dbp, markdown=True):
        choicesStr = asmChoice(item['choices'])
        db = DB(dbp)
        dbStr = db.defaultSerialization(markdown=markdown)
        return dbStr, choicesStr, choiceMap[item['rightIdx']]

    def qaTest(self, model, markdown=True, gapsec=0):
        qaList = JS(self.qaPath).loadJS()
        result = []
        for qa in tqdm(qaList, f'{self.dbn} table QA testing...'):
            dbStr, choicesStr, rightChoice = BenchmarkDB.formPrompt(qa, self.dbp, markdown)
            question = qa['question']
            fullQuestion = f'# {self.dbn}\n\n{dbStr}\n\n{question}\n\n{choicesStr}'
            prompt = singleChoicePrompt.format(question=fullQuestion)
            pred = ''
            error = None
            try:
                res = gptCall(model, prompt, f'qa_{self.hashCode}', self.logRoot)
                pred = extractAnswer(res)
            except Exception as e:
                error = str(e)
            result.append({
                'model': model,
                'markdown': markdown,
                'qtype': qa['qtype'],
                'gt': rightChoice,
                'pred': pred,
                'error': error
            })
            sleep(gapsec)
        JS(self.qaResult).newJS(result)

    @staticmethod
    def qaCount(dbRoot, model, markdown=True):
        result = {
            'row_match': [0, 0, 0],
            'item_select': [0, 0, 0],
            'count': [0, 0, 0],
            'average': [0, 0, 0],
            'sum': [0, 0, 0],
            'total': [0, 0, 0]
        }
        hashNames = os.listdir(dbRoot)
        for hn in hashNames:
            resultPath = os.path.join(dbRoot, hn, 'result')
            if not os.path.isdir(resultPath):
                continue
            jsNames = [item for item in os.listdir(resultPath) if item.startswith('TableQA')]
            for jsn in jsNames:
                jsp = os.path.join(resultPath, jsn)
                lst = JS(jsp).loadJS()
                for res in lst:
                    if model != res['model'] or markdown != res['markdown']:
                        continue
                    if res['error'] is not None:
                        result[res['qtype']][1] += 1
                    if res['pred'] == res['gt']:
                        result[res['qtype']][0] += 1
                    result[res['qtype']][2] += 1
        for k, v in result.items():
            if k == 'total':
                continue
            result['total'][0] += v[0]
            result['total'][1] += v[1]
            result['total'][2] += v[2]
        pprint(result)


if __name__ == '__main__':
    dbRoot = 'dataset/symbolic'
    dbn = 'restaurant'
    models = ['gpt-4o-mini', 'gpt-4o']
    markdown = True
    srcRoot = os.path.join(dbRoot, 'csv128k', dbn)
    dstRoot = os.path.join(dbRoot, '8k', dbn)
    os.makedirs(dstRoot, exist_ok=True)
    for i in range(10):
        tokenBasedSample(
            os.path.join(srcRoot, f'{dbn}.sqlite'),
            dstRoot,
            4 * 1024,
            6 * 1024,
            32,
            markdown
        )
        newRoot = os.path.join(dstRoot, str(i))
        os.rename(os.path.join(dstRoot, dbn), newRoot)
        bdb = BenchmarkDB(newRoot, dbn)
        bdb.qaGen()
        for model in models:
            if model.endswith('mini'):
                bdb.qaTest(model, markdown, 0)
            else:
                bdb.qaTest(model, markdown, 30)
    for model in models:
        BenchmarkDB.qaCount(dstRoot, model, markdown)
