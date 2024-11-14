python local_infer2.py \
   --model_name_or_path ../models/models--Qwen--Qwen2.5-7B-Instruct/snapshots/bb46c15ee4bb56c5b63245ef50fd7637234d6f75 \
   --model_name Qwen2.5-7B-Instruct \
   --cuda_visible 1,2 \
   --test_datasets cpads ctads \
   --test_scales 8k 16k 32k 64k \
   --output_dir ./result