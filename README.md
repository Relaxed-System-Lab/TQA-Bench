# Table Benchmark

## Data Download

Download data from the [link](https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/EZFNFZnjG6hLhULwJwLT3AQBiGVlkUMSCPo73GwIp-3tBw?e=FbnPy2) to the `dataset` directory. Then unzip it.

## Data Loader

You can use `xxxLoader.py` file in the `BenchmarkLoader` directory to load the dataset you want. There is a example in the `loadData.py` .

In the every task's datasets. I only remain the minimum part of the question. For example, in the TableQA task. I only form the structure as follows.

```markdown
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
```

Since I want to keep the prompt except the dataset is adjustable. For example, you can add some beginning prompt like `You are a professor in data analysis` and add some end prompt like `Please form the final choice in ... format` as you want.

All dataset except `EMDataset` have the parameter `scale` and `markdown` . The `scale` can be choose from `16k, 32k, 64k, 128k` , which means the total token size of the database serialized in markdown. And the `markdown` can be choose from `True, False` , which means whether the table should be formed in markdown format. If not, the table will be formed in the CSV format.
