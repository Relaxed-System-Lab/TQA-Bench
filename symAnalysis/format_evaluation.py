import sqlite3
from statsmodels.stats.contingency_tables import mcnemar

import sys

sys.path.append(".")
from symbolic import dataDict


def calculate_data(cur, db_name, scale, model):
    tables = [[0, 0], [0, 0]]
    for i in range(5):
        for j in range(14):
            cur.execute(
                f"SELECT markdown, correct FROM '{db_name}' WHERE scale='{scale}' AND model='{model}' AND dbIdx={i} AND questionIdx={j} AND sampleIdx=0 ORDER BY markdown;"
            )
            data = cur.fetchall()
            if len(data) != 2 or data[0][0] == data[1][0]:
                continue
            tables[data[0][1]][data[1][1]] += 1
    return tables


if __name__ == "__main__":
    conn = sqlite3.connect("tmp.sqlite")
    # conn = sqlite3.connect("symDataset/results/TableQA/tmp.sqlite")
    cur = conn.cursor()
    modelList = (
        "Qwen2.5-7B-Instruct Qwen2.5-Coder-7B-Instruct Llama3.1-8B-Instruct".split()
    )

    # cur.execute("SELECT DISTINCT(model) FROM airline WHERE scale='8k';")
    # print(cur.fetchall())

    for model in modelList:
        for scale in "8k 16k 32k 64k".split():
            tables = [[0, 0], [0, 0]]
            for db_name in dataDict.keys():
                curr_table = calculate_data(cur, db_name, scale, model)
                tables[0][0] += curr_table[0][0]
                tables[0][1] += curr_table[0][1]
                tables[1][0] += curr_table[1][0]
                tables[1][1] += curr_table[1][1]
            # print(tables)
            result = mcnemar(tables, exact=False, correction=True)
            print(tables)
            print(
                "model=",
                model,
                "scale=",
                scale,
                "chi2 =",
                result.statistic,
                "p-value =",
                result.pvalue,
            )
        #     for item in data:
        #         counts[item[0]] += item[1]
        # table = [[counts[3], counts[2]], [counts[1], counts[0]]]
