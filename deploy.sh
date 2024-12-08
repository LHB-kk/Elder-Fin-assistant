#!/bin/bash
LLM_MODEL_PATH=model_path_1
LOCAL_MODEL_PATH=model_path_2

# 检查是否提供了参数
if [ $# -eq 0 ]; then
    echo "请提供要部署的模型类型"
    exit 1
fi

# 根据参数选择模型路径
case $1 in
    "LLM_MODEL_PATH")  
        CUDA_VISIBLE_DEVICES=1 vllm serve $LLM_MODEL_PATH \
            --tensor-parallel-size 1 \
            --max-model-len 512 \
            --gpu-memory-utilization 0.8 \
            --swap-space 16 \
            --served-model-name model_name\
            --port 8000 \
            --trust-remote-code
        ;;
    "LOCAL_MODEL_PATH")
        CUDA_VISIBLE_DEVICES=2 vllm serve $LOCAL_MODEL_PATH \
            --tensor-parallel-size 1 \
            --max-model-len 512 \
            --gpu-memory-utilization 0.5 \
            --swap-space 16 \
            --served-model-name model_name\
            --port 8001 \
            --trust-remote-code
        ;;
    "xinference")
        xinference-local --host 0.0.0.0 --port 9997
        ;;
    "embedding")
        CUDA_VISIBLE_DEVICES=3 xinference launch --model-name model_name --model-format pytorch  --model-type embedding  --model-engine transformer
        ;;
    "register")
        xinference register --model-type embedding  --file ./config/embedding.json --persist --endpoint http://localhost:9997
        ;;
    *)
        echo "无效的模型类型：$1"
        exit 1
        ;;
esac





