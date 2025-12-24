import os
import sqlite3
import argparse
import pandas as pd

import sys

sys.path.append(".")
from symDataloader.utils import TaskCore

questionTypes = {
    "row_match": [0, 5],
    "item_select": [1, 6],
    "count": [2, 7],
    "sum": [4, 9],
    "average": [3, 8],
    "difference": [10, 11],
    "correlation": [12, 13],
}


class ResultAnalysis:
    tableNameQuery = "SELECT name FROM sqlite_master WHERE type='table';"
    allRowsQueryTemplate = "SELECT * FROM {tn} WHERE message<>'';"

    def __init__(self, dst):
        self.conn = sqlite3.connect(dst)
        self.cur = self.conn.cursor()

    def mergeTables(self, src):
        if os.path.isdir(src):
            dbNames = [item for item in os.listdir(src) if item.endswith(".sqlite")]
            for dbn in dbNames:
                dbp = os.path.join(src, dbn)
                self.mergeTables(dbp)
            return True
        conn = sqlite3.connect(src)
        cur = conn.cursor()
        cur.execute(ResultAnalysis.tableNameQuery)
        tableNames = cur.fetchall()
        if tableNames:
            tableNames = [item[0] for item in tableNames]
        else:
            return False
        for tn in tableNames:
            self.cur.execute(TaskCore.createresulttemplate.format(table_name=tn))
            cur.execute(ResultAnalysis.allRowsQueryTemplate.format(tn=tn))
            rows = cur.fetchall()
            self.cur.executemany(TaskCore.inserttemplate.format(table_name=tn), rows)
            self.conn.commit()
        return True

    @staticmethod
    def removeEmptyMessage(dbp):
        conn = sqlite3.connect(dbp)
        cur = conn.cursor()
        cur.execute(ResultAnalysis.tableNameQuery)
        tableNames = cur.fetchall()
        if tableNames:
            tableNames = [item[0] for item in tableNames]
        else:
            return False
        for tn in tableNames:
            cur.execute("DELETE FROM {tn} WHERE message='';".format(tn=tn))
            conn.commit()
        return True

    def count(self, dbLimit, questionLimit):
        self.cur.execute(ResultAnalysis.tableNameQuery)
        tableNames = self.cur.fetchall()
        if tableNames:
            tableNames = [item[0] for item in tableNames]
        else:
            return False

        mergeInstructList = []
        for tn in tableNames:
            mergeInstructList.append(
                "SELECT '{tn}', model, scale, markdown, dbIdx, sampleIdx, questionIdx, gt, pred, correct, error, message FROM {tn} WHERE message<>''".format(
                    tn=tn
                )
            )
        mergeInstruct = " UNION ALL ".join(mergeInstructList)
        self.cur.execute(
            "CREATE TEMP TABLE merged AS {mergeInstruct};".format(
                mergeInstruct=mergeInstruct
            )
        )
        self.conn.commit()

        dfs = {}
        tab = pd.read_sql(
            "SELECT markdown, model, scale, SUM(correct), COUNT(correct), SUM(correct) * 1.0 / COUNT(correct) \
        FROM merged WHERE message<>'' AND dbIdx<{dbLimit} AND sampleIdx=0 AND questionIdx<{questionLimit} GROUP BY model, scale, markdown ORDER BY markdown, model, CAST(REPLACE(scale, 'k', '') AS INTEGER);".format(
                dbLimit=dbLimit, questionLimit=questionLimit
            ),
            self.conn,
        )
        dfs["overview"] = tab

        for k, v in questionTypes.items():
            tab = pd.read_sql(
                "SELECT markdown, model, scale, SUM(correct), COUNT(correct), SUM(correct) * 1.0 / COUNT(correct) \
            FROM merged WHERE message<>'' AND dbIdx<{dbLimit} AND sampleIdx=0 AND questionIdx<{questionLimit} AND questionIdx in ({qIdx}) GROUP BY model, scale, markdown ORDER BY markdown, model, CAST(REPLACE(scale, 'k', '') AS INTEGER);".format(
                    dbLimit=dbLimit,
                    questionLimit=questionLimit,
                    qIdx=", ".join([str(it) for it in v]),
                ),
                self.conn,
            )
            dfs[k] = tab

        return dfs

    def latexTableGen(self, dbLimit, questionLimit):
        dfs = self.count(dbLimit, questionLimit)
        if dfs == False:
            return False
        modelList = dfs["overview"]["model"].unique().tolist()
        modelList.sort()
        print(modelList)
        print(len(modelList))
        # modelList = "glm-4-9b-chat DeepSeek-V2-Lite-Chat Baichuan2-7B-Chat Baichuan2-13B-Chat vicuna-7b-v1.5-16k vicuna-13b-v1.5-16k Mistral-7B-Instruct Mistral-Nemo-Instruct Llama3.1-8B-Instruct Llama-3.1-70B-Instruct Qwen2.5-3B-Instruct Qwen2.5-7B-Instruct Qwen2.5-Coder-7B-Instruct Qwen2.5-14B-Instruct Qwen2.5-72B-Instruct gemma-2-2b-it gemma-2-9b-it gemma-2-27b-it TableGPT2-7B TableLlama gpt-4o-mini gpt-4o".split()
        # modelNames = "GLM-4-9B-Chat DeepSeek-V2-Lite-Chat Baichuan2-7B-Chat Baichuan2-13B-Chat Vicuna-7B-V1.5-16K Vicuna-13B-V1.5-16K Mistral-7B-Instruct Mistral-Nemo-Instruct Llama3.1-8B-Instruct Llama3.1-70B-Instruct Qwen2.5-3B-Instruct Qwen2.5-7B-Instruct Qwen2.5-Coder-7B-Instruct Qwen2.5-14B-Instruct Qwen2.5-72B-Instruct Gemma2-2B-It Gemma2-9B-It Gemma2-27B-It TableGPT2-7B TableLlama GPT-4o-mini GPT-4o".split()
        # modelList = "o1-mini o3-mini deepseek-r1 qwq-32b-preview".split()
        # modelNames = "GPT-o1-mini GPT-o3-mini DeepSeek-R1 QwQ-32B-Preview".split()
        # modelList = ["deepseek-v3"]
        # modelNames = ["DeepSeek-V3"]
        modelList = ["gpt-5.1"]
        modelNames = ["GPT-5.1"]
        print(len(modelList))
        qt = list(questionTypes.keys()) + ["overview"]

        print("#---8k,16k---#")
        ovo = {}
        for idx in range(len(modelList)):
            model = modelList[idx]
            vals = []
            ovo[model] = []
            for sc in ["8k", "16k"]:
                for q in qt:
                    tab = dfs[q]
                    row = tab[
                        (tab["model"] == model)
                        & (tab["scale"] == sc)
                        & (tab["markdown"] == 1)
                    ]
                    if len(row) == 0:
                        vals.append("OOC")
                    else:
                        if q == "overview":
                            ovo[model].append(row.iloc[0].tolist()[-1] * 100)
                        vals.append("%.2f" % (row.iloc[0].tolist()[-1] * 100))
            lineStr = f"{modelNames[idx]} & " + " & ".join(vals) + " \\\\"
            print(lineStr)
        print("#---32k,64k---#")
        for idx in range(len(modelList)):
            model = modelList[idx]
            vals = []
            for sc in ["32k", "64k"]:
                for q in qt:
                    tab = dfs[q]
                    row = tab[
                        (tab["model"] == model)
                        & (tab["scale"] == sc)
                        & (tab["markdown"] == 1)
                    ]
                    if len(row) == 0:
                        vals.append("OOC")
                    else:
                        if q == "overview":
                            ovo[model].append(row.iloc[0].tolist()[-1] * 100)
                        vals.append("%.2f" % (row.iloc[0].tolist()[-1] * 100))
            scAvg = "%.2f" % (sum(ovo[model]) / len(ovo[model]))
            lineStr = f"{modelNames[idx]} & " + " & ".join(vals) + " \\\\"
            print(lineStr)

        mdModels = [
            "gpt-4o",
            "gpt-4o-mini",
            "Qwen2.5-7B-Instruct",
            "Qwen2.5-Coder-7B-Instruct",
            "Llama3.1-8B-Instruct",
        ]
        print("#---8k,16k---#")
        for model in mdModels:
            vals = []
            for sc in ["8k", "16k"]:
                for q in qt:
                    tab = dfs[q]
                    row = tab[
                        (tab["model"] == model)
                        & (tab["scale"] == sc)
                        & (tab["markdown"] == 1)
                    ]
                    if len(row) == 0:
                        vals.append("-")
                    else:
                        vals.append("%.2f" % (row.iloc[0].tolist()[-1] * 100))
            lineStr = f"{model} & MD & " + " & ".join(vals) + " \\\\"
            print(lineStr)
            vals = []
            for sc in ["8k", "16k"]:
                for q in qt:
                    tab = dfs[q]
                    row = tab[
                        (tab["model"] == model)
                        & (tab["scale"] == sc)
                        & (tab["markdown"] == 0)
                    ]
                    if len(row) == 0:
                        vals.append("-")
                    else:
                        vals.append("%.2f" % (row.iloc[0].tolist()[-1] * 100))
            lineStr = f"{model} & CSV & " + " & ".join(vals) + " \\\\"
            print(lineStr)
            print("\\hline")
        print("#---32k,64k---#")
        for model in mdModels:
            vals = []
            for sc in ["32k", "64k"]:
                for q in qt:
                    tab = dfs[q]
                    row = tab[
                        (tab["model"] == model)
                        & (tab["scale"] == sc)
                        & (tab["markdown"] == 1)
                    ]
                    if len(row) == 0:
                        vals.append("-")
                    else:
                        vals.append("%.2f" % (row.iloc[0].tolist()[-1] * 100))
            lineStr = f"{model} & MD & " + " & ".join(vals) + " \\\\"
            print(lineStr)
            vals = []
            for sc in ["32k", "64k"]:
                for q in qt:
                    tab = dfs[q]
                    row = tab[
                        (tab["model"] == model)
                        & (tab["scale"] == sc)
                        & (tab["markdown"] == 0)
                    ]
                    if len(row) == 0:
                        vals.append("-")
                    else:
                        vals.append("%.2f" % (row.iloc[0].tolist()[-1] * 100))
            lineStr = f"{model} & CSV & " + " & ".join(vals) + " \\\\"
            print(lineStr)
            print("\\hline")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="To combine all result dataset together."
    )
    parser.add_argument(
        "--dst", type=str, help="The destination sqlite to save all results."
    )
    parser.add_argument(
        "--src", type=str, nargs="+", help="The list of result sqlite to combine."
    )
    args = parser.parse_args()
    if args.dst:
        ra = ResultAnalysis(args.dst)
        for src in args.src:
            ra.mergeTables(src)
    elif args.src:
        for src in args.src:
            ResultAnalysis.removeEmptyMessage(src)
    else:
        # ra = ResultAnalysis("tmp.sqlite")
        # ra = ResultAnalysis("./symDataset/results/TableQA/ds-v3-result.sqlite")
        # ra.latexTableGen(5, 14)
        # Direct prompting
        ra = ResultAnalysis("./symDataset/results/TableQA/gpt_5-1.sqlite")
        # ra = ResultAnalysis("./symDataset/results/TableQA/gpt_5-1-tool.sqlite")
        ra.latexTableGen(5, 14)
    # cnt = ra.count(dbLimit=5, questionLimit=10)
    # print(cnt)
