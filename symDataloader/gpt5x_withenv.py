import os
import io
from datetime import datetime

import requests
import simplejson as json

import sys

sys.path.append(".")

from symbolic import dataDict
from symDataloader.utils import TaskCore, extractAnswer
from benchmarkUtils.database import DB


with open("benchmarkLoader/prompts/toolcallPrompt.txt", "r") as f:
    toolcallPrompt = f.read()


def qaPrompt(question, choices):
    total_question = f"{question}\n\n{choices}"
    prompt = toolcallPrompt.format(question=total_question)
    return prompt


def upload_csv_file(
    file_name,
    file_content,
    proxies={
        "http": "socks5://127.0.0.1:7890",
        "https": "socks5://127.0.0.1:7890",
    },
    openai_api_key=None,
):
    """
    Upload a CSV file to OpenAI and return the file_id.
    """
    if openai_api_key is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {openai_api_key}",
    }
    files = {
        "file": (file_name, io.BytesIO(file_content)),
    }
    data = {
        "purpose": "assistants",
    }
    resp = requests.post(
        "https://api.openai.com/v1/files",
        headers=headers,
        files=files,
        data=data,
        proxies=proxies,
    )
    resp.raise_for_status()
    msg = resp.json()
    # print(msg) # 可以正常输出
    return msg["id"]


def gpt5_tool_call_with_csv(
    csv_tables,
    question,
    choices,
    proxies={
        "http": "socks5://127.0.0.1:7890",
        "https": "socks5://127.0.0.1:7890",
    },
    openai_api_key=None,
    extra_info=None,
):
    """
    Call GPT‑5.1 Responses API with code interpreter, attaching CSV tables as files.

    csv_tables: dict[str, str]  mapping table_name -> csv_string
    """
    log_root = "symDataset/log/"
    os.makedirs(log_root, exist_ok=True)

    if openai_api_key is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    # Upload all CSV tables and collect file ids.
    file_ids = []
    for table_name, csv_str in csv_tables.items():
        # According to the Responses API docs, context-stuffed files are
        # limited to certain extensions. We use .txt here while keeping
        # the content in CSV format so the code interpreter can parse it.
        file_name = f"{table_name}.json"
        file_id = upload_csv_file(
            file_name,
            csv_str,
            proxies=proxies,
            openai_api_key=openai_api_key,
        )
        file_ids.append(file_id)

    prompt = qaPrompt(question, choices)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    # Text plus file references go into the user message.

    bodies = {
        "model": "gpt-5.1",
        "tools": [{"type": "code_interpreter", "container": {"type": "auto", "file_ids": file_ids}}],
        "input": prompt,
    }
    if extra_info is not None:
        # All metadata values must be strings for the API
        bodies["metadata"] = {k: str(v) for k, v in extra_info.items()}

    msg = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        json=bodies,
        proxies=proxies,
    ).json()

    now_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_path = os.path.join(log_root, f"{now_str}.json")
    with open(log_path, "w") as js:
        json.dump(msg, js, indent=2)

    # Try to extract the final text answer from the response
    try:
        # Align with existing gpt5x.py parsing logic
        content = msg["output"][-1]["content"][0]["text"]
    except Exception:
        # Fallback: best-effort extraction
        content = json.dumps(msg, indent=2)
    return content


class TaskCoreWithCSV(TaskCore):
    """
    A TaskCore variant that uploads DB tables as CSV files to GPT‑5.1.
    """

    def testAll(
        self,
        model,
        dbn,
        scale,
        markdown,
        dbLimit,
        sampleLimit,
        questionLimit,
        func,
        timeSleep=0,
    ):
        """
        func should be callable as:
            func(csv_tables: dict[str, str], question: str, choices: str) -> str
        where csv_tables maps table_name to CSV string.
        """
        import time

        from tqdm import tqdm

        for dbIdx in tqdm(range(dbLimit)):
            for sampleIdx in range(sampleLimit):
                # for questionIdx in range(questionLimit):
                for questionIdx in [12, 13]:
                    if self.resultCheck(
                        dbn, model, scale, markdown, dbIdx, sampleIdx, questionIdx
                    ):
                        continue
                    item = self.loadTaskItem(dbn, scale, dbIdx, sampleIdx, questionIdx)
                    if item is None:
                        continue

                    dbp = os.path.join(self.dbRoot, scale, dbn, f"{dbIdx}.sqlite")
                    db = DB(dbp)
                    tables = db.initDataFrame()
                    csv_tables = {
                        tbn: df.to_json(index=False).encode('utf-8') for tbn, df in tables.items()
                    }

                    choicesStr = TaskCore.generateChoices(item[-4:])
                    gt = TaskCore.getRightChoices(item[-5])
                    question = item[-6]

                    pred = ""
                    error = ""
                    res = ""
                    try:
                        extra_info = {
                            "model": model,
                            "scale": scale,
                            "markdown": markdown,
                            "dbidx": dbIdx,
                            "sampleidx": sampleIdx,
                            "questionidx": questionIdx,
                            "dbn": dbn,
                        }
                        res = func(csv_tables, question, choicesStr, extra_info)
                        if isinstance(res, tuple) and len(res) == 2:
                            # allow func to return (raw_text, parsed_pred)
                            res, pred_val = res
                            if isinstance(pred_val, str) and pred_val:
                                pred = pred_val
                        if not pred:
                            pred = extractAnswer(res)
                        time.sleep(timeSleep)
                    except Exception as e:
                        print(e)
                        error = str(e)
                    self.resultCur.execute(
                        TaskCore.inserttemplate.format(table_name=dbn),
                        (
                            model,
                            scale,
                            markdown,
                            dbIdx,
                            sampleIdx,
                            questionIdx,
                            gt,
                            pred,
                            gt == pred,
                            error,
                            res,
                        ),
                    )
                    self.resultConn.commit()


def gpt5_withenv_call(csv_tables, question, choices, extra_info=None):
    """
    Helper wired to TaskCoreWithCSV.testAll as func argument.
    """
    return gpt5_tool_call_with_csv(
        csv_tables,
        question,
        choices,
        extra_info=extra_info,
    )


if __name__ == "__main__":
    dbRoot = "symDataset/scaledDB"  # path to extract symDataset.zip
    taskPath = "symDataset/tasks/TableQA/dataset.sqlite"  # TableQA's dataset.sqlite
    resultPath = "symDataset/results/TableQA/gpt_5-1_withenv.sqlite"  # result sqlite
    tc = TaskCoreWithCSV(dbRoot, taskPath, resultPath)
    for k in dataDict.keys():
        for scale in ["64k"]:
            timeSleep = 0
            tc.testAll(
                "gpt-5.1",  # The model name saved in taskPath
                k,  # dataset
                scale,  # 8k, 16k, 32k, 64k, 128k
                None,  # we do not serialize tables into text
                5,  # dbLimit
                1,  # sampleLimit
                12,  # questionLimit
                gpt5_withenv_call,
                timeSleep,
            )
