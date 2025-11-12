#!/bin/bash

# Garbage Classification API Startup Script

echo "=========================================="
echo "Starting Garbage Classification API"
echo "=========================================="

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Check if conda environment exists
if ! conda env list | grep -q "garbage-classification"; then
    echo "Error: Conda environment 'garbage-classification' not found!"
    echo "Please create the environment first:"
    echo "  conda create -n garbage-classification python=3.10 -y"
    echo "  conda activate garbage-classification"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate conda environment
echo "Activating conda environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate garbage-classification

# Check if model exists
MODEL_PATH="$PROJECT_ROOT/models/garbage_yolov8m/weights/best.pt"
if [ ! -f "$MODEL_PATH" ]; then
    echo ""
    echo "Warning: Trained model not found at: $MODEL_PATH"
    echo "Please train the model first:"
    echo "  python scripts/train_yolov8.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if category mapping exists
MAPPING_PATH="$PROJECT_ROOT/configs/category_mapping.json"
if [ ! -f "$MAPPING_PATH" ]; then
    echo "Error: Category mapping not found at: $MAPPING_PATH"
    exit 1
fi

# Start API server
echo ""
echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT/api"
python main.py
