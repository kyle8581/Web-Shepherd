#! /bin/bash

########################################################
## YOUR SETTINGS
API_KEY="YOUR_API_KEY"

MODEL_NAME="WebShepherd/WebShepherd_8B"
BASE_URL="YOUR_BASE_URL"    # vllm server


SAVE_MODEL_NAME="WebShepherd"

## Evaluation Config
# web_shepherd : judge_with_checklist_generation, judge_with_gt_checklist
PROMPT_TYPE="web_shepherd"
EVALUATION_MODE="judge_with_gt_checklist"

# text_only, image_only, text_image
INPUT_TYPE="text_only"


NUM_GENERATE=5

# 0.0 ~ 1.0
TEMPERATURE=1.0
# True, False
USE_LOGPROBS=True

## Others
NUM_WORKERS=20
DATASET_NAME="WebShepherd/WebRewardBench"
SAVE_DIR="results_benchmark"
########################################################

python src/evaluate_web_reward_bench.py \
    --dataset_name $DATASET_NAME \
    --save_dir $SAVE_DIR \
    --save_model_name $SAVE_MODEL_NAME \
    --model_name $MODEL_NAME \
    --base_url $BASE_URL \
    --api_key $API_KEY \
    --num_generate $NUM_GENERATE \
    --evaluation_mode $EVALUATION_MODE \
    --prompt_type $PROMPT_TYPE \
    --input_type $INPUT_TYPE \
    --temperature $TEMPERATURE \
    --num_workers $NUM_WORKERS \
    --use_log_probs $USE_LOGPROBS \
    # --num_data 1 \