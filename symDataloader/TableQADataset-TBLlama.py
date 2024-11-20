import random
import sys
import re
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import argparse
from datetime import datetime
# import warnings

# warnings.filterwarnings('ignore')

sys.path.append('..')
from symDataloader.utils import TaskCore
from benchmarkLoader import singlePrompt

start_time = datetime.now()

def parse_args():
    parser = argparse.ArgumentParser(
        description=
        "Test with local inference")
    parser.add_argument(
        "--model_name_or_path",
        type=str,
        help=
        "Path to pretrained model or model identifier from huggingface.co/models.",
        required=True,
    )
    parser.add_argument(
        "--model_name",
        type=str,
        help=
        "model name shown in result file",
        required=True,
    )
    parser.add_argument("--seed",
                        type=int,
                        default=1234,
                        help="A seed for reproducible training.")
    parser.add_argument("--cuda_visible",
                        type=str,
                        default="0",
                        help="Index of GPU to use")
    parser.add_argument("--test_scales",
                        nargs='+', 
                        type=str, 
                        default=['16k'],
                        help="list of scales of test datasets. choose from'16k', '32k', '64k', '128k'")
    args = parser.parse_args()

    return args

args = parse_args()
os.environ["HF_DATASETS_CACHE"] = args.model_name_or_path
os.environ["HF_HOME"] = args.model_name_or_path
os.environ["HF_HUB_CACHE"] = args.model_name_or_path
os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda_visible

PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Input:\n{input_seg}\n\n### Question:\n{question}\n\n### Response:"
    ),
    "prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Response:"
    ),
}

test_scales = args.test_scales
tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=False, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(args.model_name_or_path, device_map="auto", torch_dtype="auto", low_cpu_mem_usage=True, trust_remote_code=True).eval()

def qaPrompt(dbStr, question, choices):
    totalQuestion = f'{dbStr}\n\n{question}\n\n{choices}'
    prompt = singlePrompt.format(question=totalQuestion)
    return prompt

def generate_prompt(instruction, question, input_seg=None):
  if input:
    return PROMPT_DICT["prompt_input"].format(instruction=instruction, input_seg=input_seg, question=question)
  else:
    return PROMPT_DICT["prompt_no_input"].format(instruction=instruction)

def single_inference(dbStr, question, choices):
    instruction = "Please carefully analyze and answer the following single choice question step by step. This question has only one correct answer. Please break down the question, evaluate each option, and explain why it is correct or incorrect. Conclude with your final choice on a new line formatted as `Answer: A/B/C/D`."
    prompt = generate_prompt(instruction, question+"\n\n"+choices, dbStr)     
    inputs = tokenizer(prompt, return_tensors="pt").to('cuda')

    output = model.generate(
        **inputs,
        max_new_tokens=1000,
        temperature=0.6,
        top_p=0.9,
        use_cache=True
    )
    out = tokenizer.decode(output[0], skip_special_tokens=False, clean_up_tokenization_spaces=False)
    out = out.split(prompt)[1].strip()

    return out

if __name__ == '__main__':
    dbRoot = '/app/TableBenchmark/symDataset/scaledDB' # path to extract symDataset.zip
    taskPath = '/app/TableBenchmark/symDataset/tasks/TableQA/dataset.sqlite' # TableQA's dataset.sqlite
    save_file_path = '/app/TableBenchmark/symDataset/results/TableQA/'
    resultPath = save_file_path + args.model_name + '-result.sqlite' # result sqlite
    data_lst = [
        'airline',
        'food_inspection',
        'movie',
        'music_tracker',
        'restaurant',
        'university',
        'cookbook',
        'food_facility_inspections',
        'water_quality',
        'global_biodiversity'
    ]
    tc = TaskCore(dbRoot, taskPath, resultPath)
    for dataset in data_lst:
        for test_scale in test_scales:
            tc.testAll(args.model_name, # The model name saved in taskPath
                dataset, # dataset
                test_scale, # 8k, 16k, 32k, 64k
                True, # if use markdown
                5, # dbLimit, 5 is ok
                1, # sampleLimit, 1 is ok
                14, # questionLimit, 14 is ok
                single_inference)
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
