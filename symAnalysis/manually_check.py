import sqlite3

import sys

sys.path.append(".")
from symbolic import dataDict


def check_empty(cur, model):
    all = []
    for dbn in dataDict:
        cur.execute(
            f"SELECT pred, message, gt FROM '{dbn}' WHERE scale='8k' AND model='{model}' AND dbIdx<5 AND sampleIdx=0 AND markdown=1 AND correct=0;"
        )
        all.extend([item for item in cur.fetchall()])

    empty = [item for item in all if item[0] == ""]
    print(len(all), len(empty))

    # idx = 6
    # print(empty[idx][1], empty[idx][0], empty[idx][2])


models = "Qwen2.5-7B-Instruct gpt-4o qwq-32b-preview glm-4-9b-chat".split()


if __name__ == "__main__":
    conn = sqlite3.connect("tmp.sqlite")
    cur = conn.cursor()

    # cur.execute("SELECT DISTINCT model FROM airline;")
    # models = [item[0] for item in cur.fetchall()]
    # print(len(models))

    for m in models:
        check_empty(cur, m)
