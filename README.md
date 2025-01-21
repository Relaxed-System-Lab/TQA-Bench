# Table Benchmark

## Data Preparation

**Please put the downloaded file to specific folders (create them if not exist) .**

Task file download

- Download from [task link](https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/EWAnhWoIhJpIgkkge1ZoBoYB7eF1AgJbcfV4nDfpFLua4A?e=727pOz) .

- Put the downloaded file into `symDataset/tasks/TableQA`

Download scaled database files

- Download from [scaled database link](https://hkustconnect-my.sharepoint.com/:u:/g/personal/zqiuao_connect_ust_hk/ESGMS0lh1l9MirS9SvS7_E0BSpBXpml7OsCdc0oLx70b_A?e=AgHy9i) .

- Put the downloaded file into `symDataset/scaledDB` and unzip it.

## Data Format

The scaled dataset is separated into 4 scales `8k` to `64k` , all of which are sampled from `128k` . Every scale has 10 different databases and every database have 10 different sample instances (indexing from 0 to 9) .

The task database have ten tables, each table has the following schema

```SQL
CREATE TABLE {database_name} (
    scale TEXT,           /* 8k to 64k */
    dbIdx INTEGER,        /* 0 to 9 */
    sampleIdx INTEGER,    /* 0 to 9 */
    questionIdx INTEGER,  /* 0 to 13 */
    qtype TEXT,           /* 7 types detailed in the paper */
    question TEXT,        /* question instances generated from the template */
    rightIdx INTEGER,     /* 0 to 3 refers right choice is A to D */
    A TEXT,               /* Choice A */
    B TEXT,               /* Choice B */
    C TEXT,               /* Choice C */
    D TEXT,               /* Choice D */
    PRIMARY KEY (scale, dbIdx, sampleIdx, questionIdx)
);
```

The `{database_name}` refers to the 10 databases mentioned in the scale dataset above. The `scale, dbIdx, sampleIdx, questionIdx` can be considered 4 dimensions of a question. The template question is in the `symbolic/` folder.

## Run

You can refer to `symDataloader/gpt4o.py` to see the implementation details of different models.
