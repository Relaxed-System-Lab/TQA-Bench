import torch
from transformers import AutoTokenizer

import sys
sys.path.append('.')
from benchmarkUtils.database import DB

def deepSeekCount(text):
    model_name = "deepseek-ai/DeepSeek-V2-Lite"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    inputs = tokenizer(text, return_tensors="pt")
    return inputs.input_ids.shape[-1]

if __name__ == "__main__":
    dbp = 'symDataset/scaledDB/32k/airline/0.sqlite'
    db = DB(dbp)
    dbStr = db.defaultSerialization(True)
    cnt = deepSeekCount(dbStr)
    print(cnt)
