import sqlite3

from tqabench.eval import dataList

idx = [[0, 5], [1, 6], [2, 7], [3, 8], [4, 9], [10, 11], [12, 13]]

if __name__ == "__main__":
    # dbPath = "symDataset/results/TableQA/sql1.sqlite"
    dbPath = "symDataset/results/TableQA/sql_qwen_batch1.sqlite"
    conn = sqlite3.connect(dbPath)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT(model) FROM airline;")
    models = [item[0] for item in cur.fetchall()]
    cur.execute("SELECT DISTINCT(scale) FROM airline;")
    scales = [item[0] for item in cur.fetchall()]

    for m in models:
        for s in scales:
            cor = [0 for _ in range(7)]
            cnt = [0 for _ in range(7)]
            print(m, s, end=" & ")
            for type_idx in range(7):
                for dbn in dataList:
                    cur.execute(
                        f"SELECT SUM(correct) FROM {dbn} WHERE scale='{s}' AND model='{m}' AND questionIdx IN ({idx[type_idx][0]}, {idx[type_idx][1]});"
                    )
                    curr_cor = cur.fetchall()[0][0]
                    if curr_cor is not None:
                        cor[type_idx] += curr_cor
                    else:
                        print(m, s, type_idx, dbn)
                    cur.execute(
                        f"SELECT COUNT(correct) FROM {dbn} WHERE scale='{s}' AND model='{m}' AND questionIdx IN ({idx[type_idx][0]}, {idx[type_idx][1]});"
                    )
                    curr_cnt = cur.fetchall()[0][0]
                    if curr_cnt is not None:
                        cnt[type_idx] += curr_cnt
                    else:
                        print(m, s, type_idx, dbn)
                print(f"{cor[type_idx] / cnt[type_idx] * 100:.2f}", end=" & ")
            print(f"{sum(cor) / sum(cnt) * 100:.2f}")
