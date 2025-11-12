#!/bin/bash

# Auto Pipeline: Monitor download -> Prepare dataset -> Train model

PROJECT_ROOT="/nas03/yixuh/garbage-classification"
TACO_DATA_DIR="$PROJECT_ROOT/data/raw/TACO/data"
LOG_FILE="$PROJECT_ROOT/auto_pipeline.log"

# Redirect output to log file
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=========================================="
echo "自动化流程启动"
echo "时间: $(date)"
echo "=========================================="

# Activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate garbage-classification

# Function to count downloaded images
count_images() {
    find "$TACO_DATA_DIR"/batch_* -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | wc -l
}

# Step 1: Monitor download
echo ""
echo "步骤 1: 监控图片下载"
echo "检查间隔: 10分钟"
echo "目标: 至少1000张图片"
echo ""

MIN_IMAGES=1000
CHECK_INTERVAL=600  # 10 minutes in seconds

while true; do
    CURRENT_COUNT=$(count_images)
    PERCENTAGE=$((CURRENT_COUNT * 100 / 1500))

    echo "[$(date +'%Y-%m-%d %H:%M:%S')] 当前进度: $CURRENT_COUNT/1500 张 ($PERCENTAGE%)"

    if [ "$CURRENT_COUNT" -ge "$MIN_IMAGES" ]; then
        echo ""
        echo "✓ 已下载足够的图片 ($CURRENT_COUNT 张)"
        break
    fi

    echo "  等待 10 分钟后再次检查..."
    sleep $CHECK_INTERVAL
done

# Step 2: Prepare dataset
echo ""
echo "=========================================="
echo "步骤 2: 准备数据集 (COCO -> YOLO)"
echo "时间: $(date)"
echo "=========================================="

cd "$PROJECT_ROOT"
python scripts/prepare_taco_dataset.py

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ 数据集准备失败"
    echo "请检查日志: $LOG_FILE"
    exit 1
fi

# Verify dataset
echo ""
echo "验证数据集..."
TRAIN_COUNT=$(find "$PROJECT_ROOT/data/processed/images/train" -type f 2>/dev/null | wc -l)
VAL_COUNT=$(find "$PROJECT_ROOT/data/processed/images/val" -type f 2>/dev/null | wc -l)
TEST_COUNT=$(find "$PROJECT_ROOT/data/processed/images/test" -type f 2>/dev/null | wc -l)

echo "  训练集: $TRAIN_COUNT 张"
echo "  验证集: $VAL_COUNT 张"
echo "  测试集: $TEST_COUNT 张"

if [ "$TRAIN_COUNT" -lt 100 ]; then
    echo ""
    echo "✗ 训练集图片太少 ($TRAIN_COUNT 张)"
    exit 1
fi

echo ""
echo "✓ 数据集准备完成"

# Step 3: Train model
echo ""
echo "=========================================="
echo "步骤 3: 训练模型"
echo "时间: $(date)"
echo "预计时间: 8-12 小时"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"
python scripts/train_yolov8.py

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ 模型训练失败"
    echo "请检查日志: $LOG_FILE"
    exit 1
fi

# Done
echo ""
echo "=========================================="
echo "✓ 完整流程执行完成！"
echo "完成时间: $(date)"
echo "=========================================="
echo ""
echo "模型位置: $PROJECT_ROOT/models/taco_yolov8m/weights/best.pt"
echo ""
echo "下一步: 启动API服务"
echo "  cd $PROJECT_ROOT"
echo "  ./start_api.sh"
echo ""

exit 0
