import os

import sys
sys.path.append('.')
from benchmarkLoader import BenchmarkDataset
from benchmarkUtils.jsTool import JS

class TableQADataset(BenchmarkDataset):
    def __init__(self, scale, markdown=True):
        super().__init__(scale, markdown)
        jsPath = 'dataset/task/tableQA/task.json'
        self.taskList = JS(jsPath).loadJS()

    def __getitem__(self, index):
        qa = self.taskList[index]
        question = qa['question']
        choices = qa['choices']
        choiceList = []
        for i in range(len(choices)):
            choiceList.append(f'{self.maps[i]}) {choices[i]}')
        choiceStr = '\n'.join(choiceList)
        tables = self.loadDB(qa['database']).defaultSerialization(self.markdown)
        rightChoice = self.maps[qa['rightIdx'][self.scale]]

        totalQuestion = f'# {qa["database"]}\n\n{tables}\n\n{question}\n\n{choiceStr}'
        return totalQuestion, rightChoice

    def __len__(self):
        return len(self.taskList)

if __name__ == '__main__':
    ds = TableQADataset('16k')
    for q, c in ds:
        print(q)
        print(c)
        break
