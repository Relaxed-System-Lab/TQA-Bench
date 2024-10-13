import os
import pandas as pd
from torch.utils.data import Dataset

import sys
sys.path.append('.')
from benchmarkUtils.jsTool import JS

class CPADataset(Dataset):
    def __init__(self, scale, markdown=True):
        self.scale = scale
        self.markdown = markdown
        jsPath = f'dataset/task/cpa/{self.scale}/task.json'
        self.taskList = JS(jsPath).loadJS()
        self.tableRoot = 'dataset/sotab-cpa/Validation/'
        self.maps = 'A B C D E'.split()

    def __getitem__(self, index):
        item = self.taskList[index]
        columns = item['columns']
        choices = item['choices']
        rightIdx = item['rightIdx']
        tablePath = os.path.join(self.tableRoot, item['table'])
        df = pd.read_json(tablePath, compression='gzip', lines=True)
        dfStr = ''
        if self.markdown:
            dfStr = df.to_markdown(index=False)
        else:
            dfStr = df.to_csv(index=False)

        choiceList = []
        for i in range(4):
            choiceList.append(f'{self.maps[i]}) {choices[i]}')
        choiceStr = '\n'.join(choiceList)
        question = f'{dfStr}\n\nPlease select the relevance from column {columns[0]} to column {columns[1]}.\n\n{choiceStr}'
        return question, self.maps[rightIdx]

    def __len__(self):
        return len(self.taskList)

if __name__ == '__main__':
    dl = CPADataset('16k')
    for q, c in dl:
        print(q)
        print(c)
        break
