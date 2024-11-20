import random
import sys
import re
import os
from fastchat.model import load_model, get_conversation_template, add_model_args
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
    add_model_args(parser)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--repetition_penalty", type=float, default=1.0)
    parser.add_argument("--max-new-tokens", type=int, default=1024)
    parser.add_argument("--debug", action="store_true")
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
# Reset default repetition penalty for T5 models.
if "t5" in args.model_name_or_path and args.repetition_penalty == 1.0:
    args.repetition_penalty = 1.2

test_scales = args.test_scales
model, tokenizer = load_model(
    args.model_name_or_path,
    device='cuda',
    num_gpus=3,
    max_gpu_memory=args.max_gpu_memory,
    load_8bit=False,
    cpu_offloading=args.cpu_offloading,
    revision=args.revision,
    debug=args.debug,
)
model = model.bfloat16()

def qaPrompt(dbStr, question, choices):
    totalQuestion = f'{dbStr}\n\n{question}\n\n{choices}'
    prompt = singlePrompt.format(question=totalQuestion)
    return prompt

@torch.inference_mode()
def single_inference(dbStr, question, choices):
    msg = qaPrompt(dbStr, question, choices)
    conv = get_conversation_template(args.model_name_or_path)
    conv.append_message(conv.roles[0], msg)
    conv.append_message(conv.roles[1], None)
    prompt = conv.get_prompt()
    # Run inference
    inputs = tokenizer([prompt], return_tensors="pt").to('cuda')
    output_ids = model.generate(
        **inputs,
        do_sample=True if args.temperature > 1e-5 else False,
        temperature=args.temperature,
        repetition_penalty=args.repetition_penalty,
        max_new_tokens=args.max_new_tokens,
    )

    if model.config.is_encoder_decoder:
        output_ids = output_ids[0]
    else:
        output_ids = output_ids[0][len(inputs["input_ids"][0]) :]
    outputs = tokenizer.decode(
        output_ids, skip_special_tokens=True, spaces_between_special_tokens=False
    )

    return outputs

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
