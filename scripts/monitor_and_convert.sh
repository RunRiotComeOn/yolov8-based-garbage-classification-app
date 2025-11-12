#!/bin/bash

# Monitor TACO image download and auto-convert when ready

PROJECT_ROOT="/nas03/yixuh/garbage-classification"
TACO_DATA_DIR="$PROJECT_ROOT/data/raw/TACO/data"
PROCESSED_DIR="$PROJECT_ROOT/data/processed"

echo "=========================================="
echo "TACO Dataset Download Monitor"
echo "=========================================="
echo ""

# Function to count downloaded images
count_images() {
    find "$TACO_DATA_DIR"/batch_* -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | wc -l
}

# Function to count processed images
count_processed() {
    find "$PROCESSED_DIR/images" -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | wc -l
}

# Check if download is running
DOWNLOAD_PID=$(pgrep -f "download.py.*annotations.json")

if [ -z "$DOWNLOAD_PID" ]; then
    echo "ℹ  Download script is not running."
    echo ""

    CURRENT_COUNT=$(count_images)
    echo "Current status:"
    echo "  Downloaded: $CURRENT_COUNT images"

    if [ "$CURRENT_COUNT" -lt 1000 ]; then
        echo ""
        echo "⚠  Not enough images downloaded yet."
        echo ""
        echo "To start/resume download, run:"
        echo "  cd $PROJECT_ROOT/data/raw/TACO"
        echo "  conda activate garbage-classification"
        echo "  python download.py --dataset_path ./data/annotations.json"
        exit 1
    fi
else
    echo "✓ Download is running (PID: $DOWNLOAD_PID)"
    echo ""
    echo "Monitoring download progress..."
    echo "Press Ctrl+C to stop monitoring (download will continue)"
    echo ""

    LAST_COUNT=0
    SAME_COUNT=0

    while kill -0 "$DOWNLOAD_PID" 2>/dev/null; do
        CURRENT_COUNT=$(count_images)
        PERCENTAGE=$((CURRENT_COUNT * 100 / 1500))

        printf "\rProgress: %d/1500 images (%d%%) " "$CURRENT_COUNT" "$PERCENTAGE"

        # Check if download seems stuck
        if [ "$CURRENT_COUNT" -eq "$LAST_COUNT" ]; then
            SAME_COUNT=$((SAME_COUNT + 1))
        else
            SAME_COUNT=0
        fi

        LAST_COUNT=$CURRENT_COUNT

        # If no progress for 60 seconds, warn user
        if [ "$SAME_COUNT" -ge 12 ]; then
            echo ""
            echo ""
            echo "⚠  Warning: No new images downloaded in the last 60 seconds."
            echo "   This could be normal (some images take longer) or the download may be stuck."
            SAME_COUNT=0
        fi

        sleep 5
    done

    echo ""
    echo ""
    echo "✓ Download process completed!"

    FINAL_COUNT=$(count_images)
    echo "  Total downloaded: $FINAL_COUNT images"
fi

# Check if we should convert
CURRENT_COUNT=$(count_images)

echo ""
echo "=========================================="

if [ "$CURRENT_COUNT" -lt 1000 ]; then
    echo "⚠  Only $CURRENT_COUNT images available."
    echo "   Recommended: at least 1000 images"
    echo ""
    read -p "Continue with conversion anyway? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Conversion cancelled."
        exit 0
    fi
fi

# Check if already converted
PROCESSED_COUNT=$(count_processed)

if [ "$PROCESSED_COUNT" -gt 0 ]; then
    echo "ℹ  Found $PROCESSED_COUNT processed images."
    echo ""
    read -p "Re-convert dataset? This will overwrite existing data. (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Conversion skipped."
        exit 0
    fi

    # Clean up existing processed data
    echo "Cleaning up existing processed data..."
    rm -rf "$PROCESSED_DIR/images/train/"*
    rm -rf "$PROCESSED_DIR/images/val/"*
    rm -rf "$PROCESSED_DIR/images/test/"*
    rm -rf "$PROCESSED_DIR/labels/train/"*
    rm -rf "$PROCESSED_DIR/labels/val/"*
    rm -rf "$PROCESSED_DIR/labels/test/"*
fi

echo ""
echo "=========================================="
echo "Starting Dataset Conversion"
echo "=========================================="
echo ""

# Activate conda environment and run conversion
cd "$PROJECT_ROOT"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate garbage-classification

python scripts/prepare_taco_dataset.py

echo ""
echo "=========================================="

# Check result
FINAL_PROCESSED=$(count_processed)

if [ "$FINAL_PROCESSED" -gt 0 ]; then
    echo "✓ Conversion completed successfully!"
    echo "  Processed: $FINAL_PROCESSED images"
    echo ""
    echo "Next steps:"
    echo "  1. Verify dataset: python scripts/verify_environment.py"
    echo "  2. Start training: python scripts/train_yolov8.py"
else
    echo "✗ Conversion failed. No processed images found."
    echo "  Please check the error messages above."
fi

echo "=========================================="
