#!/bin/bash

CUDA_VISIBLE_DEVICES=0
MODEL_NAME_OR_PATH="WebShepherd/WebShepherd_8B"
TENSOR_PARALLEL_SIZE=1 # length of A
HOST=YOUR_HOST
PORT=YOUR_PORT

CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES python -m vllm.entrypoints.openai.api_server \
    --model $MODEL_NAME_OR_PATH \
    --tokenizer $MODEL_NAME_OR_PATH \
    --tensor-parallel-size $TENSOR_PARALLEL_SIZE \
    --trust-remote-code \
    --max_num_seqs 4 \
    --seed 42 \
    --gpu-memory-utilization 0.9 \
    --enforce-eager \
    --host $HOST \
    --port $PORT \
    --max-model-len 10000 \