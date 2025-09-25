import simplejson as json
from tqabench.utils.sqltest import TaskCore


dataList = [
    "airline",
    "food_inspection",
    "movie",
    "music_tracker",
    "restaurant",
    "university",
    "cookbook",
    "food_facility_inspections",
    "water_quality",
    "global_biodiversity",
]

with open("tqabench/templates/arcticTemplate.txt", "r") as f:
    template = f.read()


def func(question, schema):
    prompt = template.format(
        question=question,
        schema=schema,
    )
    return prompt


if __name__ == "__main__":
    dbRoot = "symDataset/scaledDB"  # path to extract symDataset.zip
    taskPath = "symDataset/tasks/TableQA/dataset.sqlite"  # TableQA's dataset.sqlite
    resultPath = "symDataset/results/TableQA/sql_qwen_batch1.sqlite"  # result sqlite
    tc = TaskCore(dbRoot, taskPath, resultPath)

    for k in dataList:
        for scale in ["8k", "16k", "32k", "64k"]:
            # tc.dataGen(
            #     "tmp-sql-ds1.jsonl",
            #     k,  # dataset
            #     scale,  # 8k, 16k, 32k, 64k, 128k
            #     5,  # dbLimit, 10 is ok
            #     1,  # sampleLimit, 1 is ok
            #     14,  # questionLimit, 14 is ok
            #     func,
            # )
            tc.dataEval(
                "tmp-sql-ds2.jsonl",
                k,  # dataset
                scale,  # 8k, 16k, 32k, 64k, 128k
                5,  # dbLimit, 10 is ok
                1,  # sampleLimit, 1 is ok
                14,  # questionLimit, 14 is ok
            )
    # with open("tmp-sql-ds1.jsonl", "r") as jsl:
    #     data = []
    #     for line in jsl:
    #         item = json.loads(line)
    #         data.append(item)
    #
    # for item in data:
    #     print(item["body"]["messages"][-1]["content"])
    #     break
    # print(len(data))
