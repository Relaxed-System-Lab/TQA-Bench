import simplejson as json
from torch.utils.data import Dataset

import sys
sys.path.append('.')
from benchmarkLoader import multiPrompt
from benchmarkUtils.jsTool import JS

class EMDataset(Dataset):
    def __init__(self):
        jsPath = 'dataset/task/em/task.json'
        self.taskList = JS(jsPath).loadJS()
        self.maps = 'A B C D E'.split()
        self.Echoice = 'E) There are no right choices above.'

    def __getitem__(self, index):
        item = self.taskList[index]
        choices = item['stmts']
        choiceList = []
        for i in range(4):
            pairStr = f'{json.dumps(choices[i][0])} | {json.dumps(choices[i][1])}'
            choiceList.append(f'{self.maps[i]}) {pairStr}')
        choiceStr = '\n'.join(choiceList)
        rightChoice = ''.join([self.maps[i] for i in item['rightIdx']])
        rightChoice = 'E' if rightChoice == '' else rightChoice
        totalQuestion = f'Please select entity matched pairs below.\n\n{choiceStr}\n{self.Echoice}'
        totalQuestion = multiPrompt.format(question=totalQuestion)
        return totalQuestion, rightChoice

    def __len__(self):
        return len(self.taskList)

if __name__ == '__main__':
    ds = EMDataset()
    for q, c in ds:
        print(q)
        print(c)
        break
