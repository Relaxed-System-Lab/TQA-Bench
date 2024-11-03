import sys
sys.path.append('.')
from benchmarkLoader import BenchmarkDataset, batchedSinglePrompt
from benchmarkUtils.jsTool import JS

class BatchedTableQADataset(BenchmarkDataset):
    def __init__(self, batchSize, scale, markdown=True):
        super().__init__(scale, markdown)
        jsPath = 'dataset/task/tableQA/task.json'
        self.taskList = JS(jsPath).loadJS()
        self.batchSize = batchSize

        # 将数据按batch存储
        self.tasks = []
        self.tasks.append([])
        for item in self.taskList:
            if len(self.tasks[-1]) == 0:
                self.tasks[-1].append(item)
            elif len(self.tasks[-1]) < self.batchSize:
                if self.tasks[-1][-1]['database'] == item['database']:
                    self.tasks[-1].append(item)
                else:
                    self.tasks.append([])
                    self.tasks[-1].append(item)
            else:
                self.tasks.append([])
                self.tasks[-1].append(item)

    def __getitem__(self, index):
        qas = self.tasks[index]
        dbn = qas[0]['database']
        db = self.loadDB(dbn)
        dbStr = db.defaultSerialization(self.markdown)
        rightChoices = []
        questionList = []
        for idx, qa in enumerate(qas):
            q = f'Question {idx}: {qa["question"]}'
            cs = '\n'.join([f'{self.maps[i]}) {qa["choices"][i]}' for i in range(4)])
            questionList.append(f'{q}\n\n{cs}')
            rightChoices.append(self.maps[qa['rightIdx'][self.scale]])
        finalQuestion = batchedSinglePrompt.format(database=f'# {dbn}\n\n{dbStr}', questions='\n\n'.join(questionList))
        return finalQuestion, rightChoices

    def __len__(self):
        return len(self.tasks)

if __name__ == '__main__':
    ds = BatchedTableQADataset(4, '16k')
    for q, c in ds:
        print(q)
        print(c)
        break
