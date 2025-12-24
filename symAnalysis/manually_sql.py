import os
import re
import random
import sqlite3
import simplejson as json

import sys

sys.path.append(".")
from symDataloader.utils import TaskCore

dataset_path = "symDataset/tasks/TableQA/dataset.sqlite"
dataset_conn = sqlite3.connect(dataset_path)
dataset_cur = dataset_conn.cursor()


def load_data(dbn, scale, dbIdx, sampleIdx, questionIdx):
    dataset_cur.execute(
        "SELECT * FROM {dbn} WHERE scale=? AND dbIdx=? AND sampleIdx=? AND questionIdx=?;".format(
            dbn=dbn
        ),
        (scale, dbIdx, sampleIdx, questionIdx),
    )
    return dataset_cur.fetchone()


pattern = re.compile(
    r"```(?:sql)?\s*(.*?)```",
    re.IGNORECASE | re.DOTALL,  # DOTALL 让 . 能匹配换行
)


def extract_query(text: str) -> str | None:
    m = pattern.search(text)
    if not m:
        return None
    return m.group(1).strip()


if __name__ == "__main__":
    cnt = 0
    all_cnt = 0
    err_cnt = 0

    save_list = []
    with open("tmp-sql-ds2.jsonl", "r") as f:
        for l in f:
            data = json.loads(l)
            custom_id = data["custom_id"]
            _, database, scale, dbIdx, sampleIdx, questionIdx = custom_id.split("-")
            content = data["response"]["body"]["choices"][0]["message"]["content"]
            query = extract_query(content)
            dbIdx = int(dbIdx)
            sampleIdx = int(sampleIdx)
            questionIdx = int(questionIdx)
            row = load_data(database, scale, dbIdx, sampleIdx, questionIdx)
            q_type = row[4]
            if (
                scale != "8k"
                or questionIdx not in [12, 13]
                or database == "water_quality"
            ):
                continue
            all_cnt += 1

            # TODO: 进行测试
            question = row[5]
            right_idx = row[6]
            right_choice = row[7 + right_idx]
            dbp = f"symDataset/scaledDB/{scale}/{database}/{dbIdx}.sqlite"

            correct = False
            error = False
            pred = None
            try:
                conn = sqlite3.connect(dbp)
                cur = conn.cursor()
                cur.execute(query)
                pred = cur.fetchone()[0]
                if right_choice == "nan" and pred is None:
                    cnt += 1
                    correct = True
                elif abs(float(pred) - float(right_choice)) < 1e-6:
                    cnt += 1
                    correct = True
            except:
                error = True
                err_cnt += 1
            if correct is False:
                save_list.append(
                    {
                        "type": 9,
                        "db": custom_id,
                        "question": f"{q_type}: {question}",
                        "answer": right_choice,
                        "pred": str(pred),
                        "query": query,
                        "correct": correct,
                        "error": error,
                    }
                )

    print(all_cnt, cnt, err_cnt)
    print(len(save_list))

    random.shuffle(save_list)
    with open("symDataset/random_selected_sql.json", "w") as js:
        json.dump(save_list[:25], js, indent=2)
