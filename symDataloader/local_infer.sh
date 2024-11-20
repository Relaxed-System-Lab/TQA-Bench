# python TableQADataset-Fred.py \
#    --model_name_or_path /app/models/models--Qwen--Qwen2.5-Coder-7B-Instruct/snapshots/014013f208b0d052dcd0b62bf35efeb573322498 \
#    --model_name Qwen2.5-Coder-7B-Instruct \
#    --cuda_visible 6,7 \
#    --test_scales 8k 16k 32k 64k

# python TableQADataset-Fred.py \
#    --model_name_or_path /app/models/models--Qwen--Qwen2.5-7B-Instruct/snapshots/bb46c15ee4bb56c5b63245ef50fd7637234d6f75 \
#    --model_name Qwen2.5-7B-Instruct \
#    --cuda_visible 0,1,2,6 \
#    --test_scales 8k 16k 32k 64k

# python TableQADataset-Fred.py \
#    --model_name_or_path /app/models/models--meta-llama--Llama-3.1-8B-Instruct/snapshots/0e9e39f249a16976918f6564b8830bc894c89659 \
#    --model_name Llama3.1-8B-Instruct \
#    --cuda_visible 3,4,5 \
#    --test_scales 8k 16k 32k 64k





# python TableQADataset-Baichuan.py \
#    --model_name_or_path /app/models/models--baichuan-inc--Baichuan2-7B-Chat/snapshots/ea66ced17780ca3db39bc9f8aa601d8463db3da5 \
#    --model_name Baichuan2-7B-Chat \
#    --cuda_visible 0,1,7 \
#    --test_scales 8k 16k 32k 64k

# python TableQADataset-Fred.py \
#    --model_name_or_path /app/models/models--Qwen--Qwen2.5-3B-Instruct/snapshots/aa8e72537993ba99e69dfaafa59ed015b17504d1 \
#    --model_name Qwen2.5-3B-Instruct \
#    --cuda_visible 2,6 \
#    --test_scales 8k 16k 32k 64k

# python TableQADataset-Fred.py \
#    --model_name_or_path /app/models/models--THUDM--glm-4-9b-chat/snapshots/eb55a443d66541f30869f6caac5ad0d2e95bcbaa \
#    --model_name glm-4-9b-chat \
#    --cuda_visible 3,4,5 \
#    --test_scales 8k 16k 32k 64k

# CUDA_VISIBLE_DEVICES=2,6,7 python TableQADataset-vicuna.py\
#    --model_name_or_path /app/models/models--lmsys--vicuna-7b-v1.5/snapshots/3321f76e3f527bd14065daf69dad9344000a201d \
#    --model_name vicuna-7b-v1.5 \
#    --cuda_visible 2,6,7 \
#    --test_scales 8k 16k\
#    --max-gpu-memory 24GiB

# python TableQADataset-Fred.py \
#    --model_name_or_path /app/models/models--tablegpt--TableGPT2-7B/snapshots/9de1c2116151f6ccc6915616f625bb9c365dd9ba \
#    --model_name TableGPT2-7B \
#    --cuda_visible 0,1 \
#    --test_scales 8k 16k 32k 64k

python TableQADataset-TBLlama.py \
   --model_name_or_path /app/models/models--osunlp--TableLlama/snapshots/b4bd8bac8b7570dcfa01ca3ef4f8fd0ffef957ed \
   --model_name TableLlama \
   --cuda_visible 2,3 \
   --test_scales 8k



# python TableQADataset-CaseStudy.py \
#    --model_name_or_path /app/models/models--Qwen--Qwen2.5-7B-Instruct/snapshots/bb46c15ee4bb56c5b63245ef50fd7637234d6f75 \
#    --model_name Qwen2.5-7B-Instruct \
#    --cuda_visible 0,1,2,6 \
#    --test_scales 8k