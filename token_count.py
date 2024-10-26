from benchmarkLoader.tableQALoader import TableQADataset
from benchmarkLoader.tableFVLoader import TableFVDataset
from benchmarkLoader.retrievalLoader import RetrievalDataset
from benchmarkLoader.cpaLoader import CPADataset
from benchmarkLoader.ctaLoader import CTADataset
from benchmarkLoader.emLoader import EMDataset

import re

import os
import sys
# os.environ["CUDA_VISIBLE_DEVICES"] = "0, 1, 2, 3"

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

import tiktoken
# To get the tokeniser corresponding to a specific model in the OpenAI API:
tokenizer = tiktoken.encoding_for_model("gpt-4o")

def extractAnswer(text:str)->str:
    patt = r'answer:\s*([A-F]+)'
    grps = re.findall(patt, text, re.IGNORECASE)
    if grps:
        return grps[-1].upper()
    return ''

if __name__ == '__main__':

    max_L = '16k'
    qads = TableQADataset(max_L, True)
    fvds = TableFVDataset(max_L, True)
    retds = RetrievalDataset(max_L, True)
    cpads = CPADataset(max_L, True)
    ctads = CTADataset(max_L, True)

    print('qads', len(qads))
    print('fvds', len(fvds))
    print('retds', len(retds))
    print('cpads', len(cpads))
    print('ctads', len(ctads))
    # print('emds', len(emds))

    total_num = 0
    total_num += len(qads) + len(fvds) + len(retds) + len(cpads) + len(ctads)

    print(f"max_L = {max_L}; total_num = {total_num}")

    test_result = []
    idx = 0

    datasets = [qads, fvds, retds, cpads, ctads]
    datasets_names = ["qads", "fvds", "retds", "cpads", "ctads"]
    
    all_token_num = 0
    all_test_num = 0
    for dataset, dataset_name in zip(datasets, datasets_names):
        dataset_token_num = 0
        dataset_test_num = 0
        for question, rightChoice in dataset:
            token_num = len(tokenizer.encode(text=question))
            dataset_token_num += token_num
            dataset_test_num += 1
        print(f"Dataset: {dataset_name}; token_num: {dataset_token_num}; test_num: {dataset_test_num}; avg_token_num = {(dataset_token_num / dataset_test_num):.2f}")
        all_token_num += dataset_token_num
        all_test_num += dataset_test_num
    print(f"Dataset: ALL; token_num: {all_token_num}; test_num: {all_test_num}; avg_token_num = {(all_token_num / all_test_num):.2f}")