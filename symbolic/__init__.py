import os
import re
from tqdm import tqdm

import sys
sys.path.append('.')
from benchmarkUtils.LLM import gptCall
from benchmarkUtils.database import DB
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
    ret.append(sym.q0())
    ret.append(sym.q1())
    ret.append(sym.q2())
    ret.append(sym.q3())
    ret.append(sym.q4())
    ret.append(sym.q5())
    ret.append(sym.q6())
    ret.append(sym.q7())
    ret.append(sym.q8())
    ret.append(sym.q9())
    return ret

class TableQA:
    def __init__(self, dbRoot, jsPath, logRoot, dstJs):
        self.dbr = dbRoot
        self.jsp = jsPath
        self.lr = logRoot
        self.dstJs = dstJs

    def loadDB(self, dbn):
        dbp = os.path.join(self.dbr, dbn, f'{dbn}.sqlite')
        return dbp

    def qaGen(self):
        qaDataset = {}
        for k, v in dataDict.items():
            dbp = self.loadDB(k)
            qas = symLoad(v, dbp)
            qaList = []
            for row in qas:
                if len(row) < 4:
                    continue
                question, answer, rightIdx, choices = row[:4]
                choices = [str(it) for it in choices]
                item = {
                    'question': question,
                    'rightIdx': rightIdx,
                    'choices': choices
                }
                qaList.append(item)
            if len(qaList) == 0:
                continue
            qaDataset[k] = {
                'dbp': dbp,
                'qas': qaList
            }
        JS(self.jsp).newJS(qaDataset)
        return qaDataset

    @staticmethod
    def formPrompt(item, dbp, markdown=True):
        choicesStr = asmChoice(item['choices'])
        question = item['question']
        db = DB(dbp)
        dbStr = db.defaultSerialization(markdown=markdown)
        totalQuestion = f'{dbStr}\n\n{question}\n\n{choicesStr}'
        asmQuestion = singleChoicePrompt.format(question=totalQuestion)
        return asmQuestion, choiceMap[item['rightIdx']]

    def test(self, markdown=True):
        if not os.path.isfile(self.jsp):
            self.qaGen()
        qaDataset = self.qaGen()

        testset = []
        for k, v in qaDataset.items():
            dbp = v['dbp']
            for item in v['qas']:
                q, c = TableQA.formPrompt(item, dbp, markdown)
                testset.append((q, c))

        if not os.path.isfile(self.dstJs):
            result = []
            for idx in tqdm(range(len(testset)), 'TableQA Testing...'):
                q, c = testset[idx]
                pred = ''
                error = None
                try:
                    res = gptCall('gpt-4o-mini', q, 'tmp', self.lr)
                    pred = extractAnswer(res)
                except Exception as e:
                    error = str(e)
                result.append({
                    'idx': idx,
                    'pred': pred,
                    'gt': c,
                    'error': error
                })
            JS(self.dstJs).newJS(result)
        cnt = acc(self.dstJs)
        print(cnt)

if __name__ == '__main__':
    qa = TableQA('dataset/optmizedScaledDB/8k', 'tmp.json', 'tmp/symlog/test', 'dst.json')
    qa.test()
