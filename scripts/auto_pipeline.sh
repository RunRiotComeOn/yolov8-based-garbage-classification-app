#!/bin/bash

# Auto Pipeline: Monitor download -> Prepare dataset -> Train model

PROJECT_ROOT="/nas03/yixuh/garbage-classification"
TACO_DATA_DIR="$PROJECT_ROOT/data/raw/TACO/data"
LOG_FILE="$PROJECT_ROOT/auto_pipeline.log"

# Redirect output to log file
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=========================================="
echo "Pipeline started"
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
echo "Step 1: Monitor download"
echo ""

MIN_IMAGES=1000
CHECK_INTERVAL=600  # 10 minutes in seconds

while true; do
    CURRENT_COUNT=$(count_images)
    PERCENTAGE=$((CURRENT_COUNT * 100 / 1500))

    echo "[$(date +'%Y-%m-%d %H:%M:%S')]  $CURRENT_COUNT/1500 ($PERCENTAGE%)"
done

# Step 2: Prepare dataset
echo ""
echo "=========================================="
echo "Step 2: Prepare dataset"
echo "=========================================="

cd "$PROJECT_ROOT"
python scripts/prepare_taco_dataset.py


# Verify dataset
echo ""
echo "Verifying dataset..."
TRAIN_COUNT=$(find "$PROJECT_ROOT/data/processed/images/train" -type f 2>/dev/null | wc -l)
VAL_COUNT=$(find "$PROJECT_ROOT/data/processed/images/val" -type f 2>/dev/null | wc -l)
TEST_COUNT=$(find "$PROJECT_ROOT/data/processed/images/test" -type f 2>/dev/null | wc -l)

echo "  Train: $TRAIN_COUNT"
echo "  Val: $VAL_COUNT"
echo "  Test: $TEST_COUNT"

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
echo "Step 3: Train model"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"
python scripts/train_yolov8.py

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Training failed"
    echo "Please check log file: $LOG_FILE"
    exit 1
fi

# Done
echo ""
echo "=========================================="
echo "✓ Pipeline completed successfully"
echo "=========================================="
echo ""
echo "Best model checkpoint: $PROJECT_ROOT/models/taco_yolov8m/weights/best.pt"
echo ""
echo "Next step: API server"
echo "  cd $PROJECT_ROOT"
echo "  ./start_api.sh"
echo ""

exit 0
