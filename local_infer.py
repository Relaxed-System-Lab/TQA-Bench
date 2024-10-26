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

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from utils import construcrt_dataset,create_folder_if_not_exists, append_into_jsonl_file

import argparse

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
    parser.add_argument("--output_dir",
                        type=str,
                        default=None,
                        help="Where to store the result.")
    parser.add_argument("--seed",
                        type=int,
                        default=1234,
                        help="A seed for reproducible training.")
    parser.add_argument("--cuda_visible",
                        type=str,
                        default="0",
                        help="Index of GPU to use")
    parser.add_argument("--test_datasets",
                        nargs='+', 
                        type=str, 
                        default=['qads'],
                        help="list of names of test datasets. choose from'qads', 'fvds', 'retds', 'cpads', 'ctads'")
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


def extractAnswer(text:str)->str:
    patt = r'answer:\s*([A-F]+)'
    grps = re.findall(patt, text, re.IGNORECASE)
    if grps:
        return grps[-1].upper()
    return ''

if __name__ == '__main__':
    test_datasets = args.test_datasets
    test_scales = args.test_scales

    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, use_fast=False)
    model = AutoModelForCausalLM.from_pretrained(args.model_name_or_path, device_map="auto", torch_dtype="auto").eval()

    for test_dataset in test_datasets:
        for test_scale in test_scales:
            print(f"construct dataset {test_dataset} with scale {test_scale}")
            dataset = construcrt_dataset(test_dataset, test_scale)
            save_file_path = args.output_dir + f"/{test_dataset}/{test_scale}/"
            create_folder_if_not_exists(save_file_path)

            for idx, (question, rightChoice) in enumerate(dataset):
                prompt = "<|im_start|>user\n" + question + "<|im_end|>\n<|im_start|>assistant\n"
                try:
                    input_ids = tokenizer.encode(text=prompt, return_tensors='pt')
                    with torch.no_grad():
                        output_ids = model.generate(input_ids.to('cuda'), max_new_tokens = 3000, eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.eos_token_id)
                    response = tokenizer.decode(output_ids[0][input_ids.shape[1]:], skip_special_tokens=True)
                except torch.cuda.OutOfMemoryError:
                    response = f"Out of memory error in dataset {test_dataset} with scale {test_scale} at index {idx}"
                    torch.cuda.empty_cache()
                except Exception as e:
                    response = f"Unexpected error in dataset {test_dataset} with scale {test_scale} at index {idx}"
                
                print(f"{idx}: partial response = {response[:200]}...")
                jsonl_data = {
                    "model_path": args.model_name_or_path,
                    "dataset": test_dataset,
                    "scale": test_scale,
                    "index": idx,
                    "response": response
                }
                append_into_jsonl_file(save_file_path + 'result.jsonl', jsonl_data)