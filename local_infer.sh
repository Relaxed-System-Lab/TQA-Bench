python local_infer.py \
   --model_name_or_path /home/gxhe/models/models--01-ai--Yi-1.5-9B-Chat-16K/snapshots/2f8753bed95bd4fede3fd64f8305428620b4b212 \
   --cuda_visible 0,1 \
   --test_datasets qads fvds \
   --test_scales 32k 16k \
   --output_dir ./result