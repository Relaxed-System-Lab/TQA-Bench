import tiktoken

import sys
import sqlite3

sys.path.append(".")
from symbolic import dataDict

modelDict = {
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "o1-mini": "o1",
    "o3-mini": "o3",
}


class GPTTokenizer:
    # modelName->tokenizerName
    modelDict = {
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        "o1-mini": "o1",
        "o3-mini": "o3",
    }

    def __init__(self, modelName):
        assert modelName in GPTTokenizer.modelDict.keys(), (
            "Please input correct model name."
        )
        self.enc = tiktoken.encoding_for_model(GPTTokenizer.modelDict[modelName])

    def restrictSize(self, text, sz):
        return self.enc.decode(self.enc.encode(text)[:sz])


def correctGPTModels(dbPath, maxSize, model):
    enc = tiktoken.encoding_for_model(modelDict[model])
    selectTemplate = "SELECT * FROM [{dbName}] WHERE model='{model}';"
    conn = sqlite3.connect(dbPath)
    cur = conn.cursor()

    tokenSize = []
    for dbName in dataDict:
        cur.execute(selectTemplate.format(dbName=dbName, model=model))
        res = cur.fetchall()
        for item in res:
            tokenSize.append(len(enc.encode(item[-1])))
    print(sum(tokenSize) / len(tokenSize))


if __name__ == "__main__":
    # correctGPTModels(
    #     "symDataset/results/TableQA/gpt_ox_reasoning.sqlite", 4096, "o1-mini"
    # )
    correctGPTModels("tmp.sqlite", 4096, "gpt-4o")
