import re
import os
import sys
sys.path.append(".")
from benchmarkLoader.tableQALoader import TableQADataset
from benchmarkLoader.tableFVLoader import TableFVDataset
from benchmarkLoader.retrievalLoader import RetrievalDataset
from benchmarkLoader.cpaLoader import CPADataset
from benchmarkLoader.ctaLoader import CTADataset
from benchmarkLoader.emLoader import EMDataset

def construcrt_dataset(dataset_name:str, dataset_scale:int):
    if dataset_name == 'qads':
        return TableQADataset(dataset_scale, True)
    if dataset_name == 'fvds':
        return TableFVDataset(dataset_scale, True)
    if dataset_name == 'retds':
        return RetrievalDataset(dataset_scale, True)
    if dataset_name == 'cpads':
        return CPADataset(dataset_scale, True)
    if dataset_name == 'ctads':
        return CTADataset(dataset_scale, True)

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        pass

import json
def append_into_jsonl_file(file_path, data_to_append):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data_to_append, ensure_ascii=False) + '\n')