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

test_scales = args.test_scales
tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(args.model_name_or_path, device_map="auto", torch_dtype="auto").eval()

def qaPrompt(dbStr, question, choices):
    totalQuestion = f'{dbStr}\n\n{question}\n\n{choices}'
    prompt = singlePrompt.format(question=totalQuestion)
    return prompt

def single_inference(dbStr, question, choices):
    prompt = qaPrompt(dbStr, question, choices)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    # try:
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to('cuda')
    with torch.no_grad():
        generated_ids = model.generate(**model_inputs, max_new_tokens=800)
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # print(len(generated_ids[0]))
    # except torch.cuda.OutOfMemoryError:
    #     response = f"Out of memory error"
    #     torch.cuda.empty_cache()
    # except Exception as e:
    #     print(e)
    #     response = f"Unexpected error"
    return response

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
                False, # if use markdown
                5, # dbLimit, 5 is ok
                1, # sampleLimit, 1 is ok
                14, # questionLimit, 14 is ok
                single_inference)
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
