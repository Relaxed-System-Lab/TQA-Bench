import os
import sys
import sqlite3
import time
from tqdm import tqdm

sys.path.append('.')
from benchmarkUtils.database import DB
from benchmarkUtils.jsTool import JS
from benchmarkUtils.LLM import gptCall
from symWorkflow.TableQA import TableQA
from symbolic import extractAnswer

createResultTemplate = """
CREATE TABLE IF NOT EXISTS {table_name} (
    model TEXT,
    scale TEXT,
    markdown INTEGER,
    dbIdx INTEGER,
    sampleIdx INTEGER,
    questionIdx INTEGER,
    gt TEXT,
    pred TEXT,
    correct INTEGER,
    error TEXT,
    message TEXT,
    PRIMARY KEY (model, scale, markdown, dbIdx, sampleIdx, questionIdx)
);
"""

primaryKeyCheck = """
SELECT 1
FROM {table_name}
WHERE model = ? AND scale = ? AND markdown = ? AND dbIdx = ? AND sampleIdx = ? AND questionIdx = ?;
"""

insertTemplate = """
INSERT OR IGNORE INTO {table_name}
(model, scale, markdown, dbIdx, sampleIdx, questionIdx, gt, pred, correct, error, message)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

def test(model, scale, dbn, markdown, dbIdx, sampleIdx, questionIdx,
         dbRoot='symDataset/scaledDB', taskRoot='symDataset/tasks/TableQA', resultRoot='symDataset/results/TableQA'):
    logRoot = os.path.join(resultRoot, 'log')
    os.makedirs(logRoot, exist_ok=True)
    dbPath = os.path.join(resultRoot, 'result.sqlite')
    conn = sqlite3.connect(dbPath)
    cur = conn.cursor()
    cur.execute(createResultTemplate.format(table_name=dbn))

    cur.execute(primaryKeyCheck.format(table_name=dbn), (model, scale, markdown, dbIdx, sampleIdx, questionIdx))
    result = cur.fetchone()
    if result:
        # 已经测试过了, 就不要进行任何的执行了
        cur.close()
        conn.close()
        return False

    datasetPath = os.path.join(taskRoot, 'dataset.sqlite')
    prompt, gt = TableQA.loadItem(datasetPath, dbRoot, dbn, scale, dbIdx, sampleIdx, questionIdx, markdown)

    pred = ''
    error = ''
    res = ''
    try:
        res = gptCall(model,
                      prompt,
                      '',
                      logRoot)
        pred = extractAnswer(res)
    except Exception as e:
        error = str(e)
    correct = pred == gt
    cur.execute(insertTemplate.format(table_name=dbn), (model, scale, markdown, dbIdx, sampleIdx, questionIdx, gt, pred, correct, error, res))
    conn.commit()
    cur.close()
    conn.close()
    return True

if __name__ == '__main__':
    testSetting = [('gpt-4o-mini', 0), ('gpt-4o', 30)]
    for sc in ['8k', '32k', '64k', '128k']:
        for ts in testSetting:
            for i in tqdm(range(10)):
                for j in range(10):
                    res = test(
                        ts[0],
                        sc,
                        'university',
                        True,
                        i,0,j # 每个数据库层面采样, 都只做1次问答
                    )
                    if not res:
                        continue
                    time.sleep(ts[1])
                    if sc != '8k':
                        time.sleep(30)
    # db = DB('symDataset/results/TableQA/result.sqlite')
    # print(db.tables)
