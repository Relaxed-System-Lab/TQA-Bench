# Table Benchmark

## Data Download

Download data from the [link](https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/EcOPRsSJQL5Kn-aFXRNgIesBsI1jR3c_8Klokr9RCSDPdg?e=zIUiCf) to the `dataset` directory. Then unzip it.

## Data Loader

You can use `xxxLoader.py` file in the `BenchmarkLoader` directory to load the dataset you want. There is a example in the `loadData.py` .

In the every task's datasets. I provide the full prompt in the xxxDataset class. The question is combined with single choice question prompt and multiple choice question prompt. For example, the Table QA task is prompt as follows.

```markdown
Please carefully analyze and answer the following single choice question step by step.

# {database name}

## {Table1}

{table1 in CSV/markdown}

## {Table2}

{table2 in CSV/markdown}

...

{question}

A) ...
B) ...
C) ...
D) ...

This question has only one correct answer. Please break down the question, evaluate each option, and explain why it is correct or incorrect. Conclude with your final choice on a new line formatted as `Answer: A/B/C/D`.
```

Since the prompt fully describes the task type and answer format. You can just load them and send them to the LLM to get the answer. For example, you can load the table QA as follows:

```python
qads = TableQADataset('16k', True)

print('qads', len(qads))

for question, rightChoice in qads:
    print(question)
    print(rightChoice)
```

Other dataset examples can be found in `loadData.py` . And I provide a simple function `extractAnswer` to extract choice from the LLM returned strings.

All dataset except `EMDataset` have the parameter `scale` and `markdown` . The `scale` can be choose from `16k, 32k, 64k, 128k` , which means the total token size of the database serialized in markdown. And the `markdown` can be choose from `True, False` , which means whether the table should be formed in markdown format. If not, the table will be formed in the CSV format.

The `EMDataset` do not have any parameters.
