import sys
sys.path.append('.')
from benchmarkLoader import BenchmarkDataset
from benchmarkUtils.jsTool import JS

class TableFVDataset(BenchmarkDataset):
    def __init__(self, scale, markdown=True):
        super().__init__(scale, markdown)
        jsPath = f'dataset/task/tableFV/{self.scale}/task.json'
        self.taskList = JS(jsPath).loadJS()
        self.Echoice = 'E) There is no right statment above.'

    def __getitem__(self, index):
        qa = self.taskList[index]
        choices = qa['stmts']
        choiceList = []
        for i in range(len(choices)):
            choiceList.append(f'{self.maps[i]}) {choices[i]}')
        choiceStr = '\n'.join(choiceList)
        tables = self.loadDB(qa['database']).defaultSerialization(self.markdown)
        rightChoice = ''.join([self.maps[i] for i in qa['rightIdx']])
        rightChoice = 'E' if rightChoice == '' else rightChoice

        totalQuestion = f'# {qa["database"]}\n\n{tables}\n\nPlease select the right statement(s).\n\n{choiceStr}\n{self.Echoice}'
        return totalQuestion, rightChoice

    def __len__(self):
        return len(self.taskList)

if __name__ == '__main__':
    ds = TableFVDataset('16k')
    for q, c in ds:
        print(q)
        print(c)
        break
