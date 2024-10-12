import sys
sys.path.append('.')
from benchmarkLoader import BenchmarkDataset
from benchmarkUtils.jsTool import JS

class RetrievalDataset(BenchmarkDataset):
    def __init__(self, scale, markdown=True):
        super().__init__(scale, markdown)
        jsPath = f'dataset/task/retrieval/task.json'
        self.taskList = JS(jsPath).loadJS()
        self.Echoice = 'E) There still need other tables to answer the question.'

    def __getitem__(self, index):
        qa = self.taskList[index]
        question = qa['question']
        choices = qa['choices']
        choiceList = []
        for i in range(len(choices)):
            choiceList.append(f'{self.maps[i]}) {choices[i]}')
        choiceStr = '\n'.join(choiceList)
        tables = self.loadDB(qa['database']).initDataFrame()
        tableList = []
        for k, v in tables.items():
            if self.markdown:
                tableList.append(f'## {k}\n\n{v.to_markdown(index=False)}')
            else:
                tableList.append(f'## {k}\n\n{v.to_csv(index=False)}')
        tables = '\n\n'.join(tableList)
        rightChoice = ''.join([self.maps[i] for i in qa['rightIdx']])
        rightChoice = f'{rightChoice}E' if qa['needOther'] else rightChoice

        totalQuestion = f'# {qa["database"]}\n\n{tables}\n\nPlease select the table(s) that can be used to answer the following question.\nQuestion: {question}\n\n{choiceStr}\n{self.Echoice}'
        return totalQuestion, rightChoice

    def __len__(self):
        return len(self.taskList)

if __name__ == '__main__':
    ds = RetrievalDataset('16k')
    for q, c in ds:
        print(q)
        print(c)
        break
