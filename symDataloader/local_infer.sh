python TableQADataset-Fred.py \
   --model_name_or_path /app/models/models--Qwen--Qwen2.5-Coder-7B-Instruct/snapshots/014013f208b0d052dcd0b62bf35efeb573322498 \
   --model_name Qwen2.5-Coder-7B-Instruct \
   --cuda_visible 6,7 \
   --test_scales 8k 16k 32k 64k

# python TableQADataset-Fred.py \
#    --model_name_or_path /app/models/models--Qwen--Qwen2.5-7B-Instruct/snapshots/bb46c15ee4bb56c5b63245ef50fd7637234d6f75 \
#    --model_name Qwen2.5-7B-Instruct \
#    --cuda_visible 0,1,2 \
#    --test_scales 8k 16k 32k 64k

# python TableQADataset-Fred.py \
#    --model_name_or_path /app/models/models--meta-llama--Llama-3.1-8B-Instruct/snapshots/0e9e39f249a16976918f6564b8830bc894c89659 \
#    --model_name Llama3.1-8B-Instruct \
#    --cuda_visible 3,4,5 \
#    --test_scales 8k 16k 32k 64k
