# Garbage Classification Detection API

A garbage classification detection API system based on YOLOv8 and Roboflow Garbage Classification Dataset

## Project Overview

This project implements an efficient and accurate backend API service that accepts user-uploaded garbage images, performs real-time object detection using a deep learning model, and returns detection results with multi-level labels.

### Core Features

- **Precise Detection**: Based on YOLOv8s model, recognizing 7 garbage categories
- **Large-Scale Dataset**: Trained on 10,464 high-quality images from Roboflow
- **Multi-Level Labels**: Provides two levels of classification labels
  - **L1 - Specific Name**: e.g., "PLASTIC", "PAPER", "METAL"
  - **L2 - Disposal Category**: e.g., "Recycle", "Trash", "Hazardous", "Organic"
- **High-Performance Training**: Optimized for RTX 6000 Ada (48GB)
- **RESTful API**: High-performance API service built with FastAPI
- **Real-Time Inference**: Fast detection with JSON-formatted results

## Tech Stack

- **Model Framework**: YOLOv8 (Ultralytics)
- **Training Dataset**: GARBAGE CLASSIFICATION 3 (Roboflow Universe)
  - 10,464 images
  - 7 classes: BIODEGRADABLE, CARDBOARD, CLOTH, GLASS, METAL, PAPER, PLASTIC
- **Backend Framework**: FastAPI
- **Deep Learning**: PyTorch
- **Training Hardware**: NVIDIA RTX 6000 Ada (48GB VRAM)

## Project Structure

```
garbage-classification/
├── api/                          # API service code
│   ├── main.py                   # FastAPI main program
│   └── test_client.py            # API test client
├── configs/                      # Configuration files
│   ├── category_mapping.json     # Category mapping file (L1 → L2)
│   └── garbage.yaml              # YOLOv8 dataset configuration
├── data/                         # Data directory
│   ├── raw/                      # Raw dataset from Roboflow
│   └── processed/                # Processed YOLO-format data
│       ├── images/               # Images
│       │   ├── train/
│       │   ├── valid/
│       │   └── test/
│       └── labels/               # Labels
│           ├── train/
│           ├── valid/
│           └── test/
├── models/                       # Trained model save directory
│   └── garbage_yolov8s/
│       └── weights/
│           ├── best.pt           # Best model
│           └── last.pt           # Last epoch model
├── scripts/                      # Script files
│   ├── download_garbage_dataset.py  # Dataset download script
│   ├── train_yolov8.py           # Model training script
│   └── verify_environment.py     # Environment verification
└── requirements.txt              # Python dependencies
```

## Quick Start

### 1. Environment Setup

```bash
# Activate conda environment
conda activate garbage-classification

# Or create a new environment if it doesn't exist
conda create -n garbage-classification python=3.10 -y
conda activate garbage-classification

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Dataset

**Option 1: Using Your Roboflow API Key (Automatic)**

```bash
# Install roboflow package
pip install roboflow

# Download dataset with your API key
python scripts/download_garbage_dataset.py --api-key sIWvnNEtbUWeBxn0ZhWq
```

**Option 2: Using Default API Key**

```bash
# Directly download without specifying API key (uses default)
python scripts/download_garbage_dataset.py
```

**Option 3: Manual Download**

```bash
# Show manual download instructions
python scripts/download_garbage_dataset.py --manual
```

1. Visit: https://universe.roboflow.com/material-identification/garbage-classification-3
2. Click 'Download Dataset'
3. Select 'YOLOv8' format
4. Download and extract to: `data/raw/`
5. Run: `python scripts/download_garbage_dataset.py --organize data/raw/GARBAGE-CLASSIFICATION-3-2`

**Option 4: Use Roboflow Serverless Inference (No Training Needed)**

If you just want to test the model without training:

```bash
# Install inference SDK
pip install inference-sdk

# Test on an image
python scripts/test_roboflow_inference.py --image path/to/image.jpg

# Compare with local model (if trained)
python scripts/test_roboflow_inference.py --image path/to/image.jpg --compare

# Batch test on multiple images
python scripts/test_roboflow_inference.py --batch path/to/image/directory
```

**Dataset Statistics**:
- Total Images: 10,464
- Train: ~8,000 images
- Valid: ~1,500 images
- Test: ~1,000 images
- Classes: 7 (BIODEGRADABLE, CARDBOARD, CLOTH, GLASS, METAL, PAPER, PLASTIC)

### 3. Train Model

```bash
# Train YOLOv8s model with optimized configuration
python scripts/train_yolov8.py
```

**Training Configuration**:
- Model: YOLOv8s (small model, fast and accurate)
- Image Size: 640x640 (standard YOLO size)
- Batch Size: 32 (optimized for A6000)
- Epochs: 150
- Device: GPU 0
- Enhanced data augmentation for better generalization

After training, the best model will be saved at: `models/garbage_yolov8s/weights/best.pt`

### 4. Start API Service

```bash
# Start FastAPI server
cd api
python main.py
```

Service will run at: `http://localhost:8000`

View API documentation: `http://localhost:8000/docs`

### 5. Test API

```bash
# Health check
python api/test_client.py --url http://localhost:8000

# Test image detection
python api/test_client.py --image /path/to/test/image.jpg --url http://localhost:8000

# Run all tests
python api/test_client.py --all --image /path/to/test/image.jpg
```

## API Usage Examples

### Health Check

```bash
curl http://localhost:8000/health
```

### Garbage Detection

```bash
curl -X POST "http://localhost:8000/v1/detect_trash" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@test_image.jpg"
```

### Response Example

```json
{
  "status": "success",
  "detection_count": 2,
  "inference_time_ms": 25.14,
  "detections": [
    {
      "bbox_xyxy": [450.2, 150.8, 520.5, 300.1],
      "confidence": 0.92,
      "specific_name": "PLASTIC",
      "general_category": "Recycle"
    },
    {
      "bbox_xyxy": [120.3, 220.5, 140.2, 235.8],
      "confidence": 0.85,
      "specific_name": "METAL",
      "general_category": "Recycle"
    }
  ]
}
```

### Get All Categories

```bash
curl http://localhost:8000/v1/categories
```

## Category Mapping

### 7 Material Categories (L1 Labels)

| Category | Description | Examples |
|----------|-------------|----------|
| BIODEGRADABLE | Organic and biodegradable waste | Food waste, organic materials |
| CARDBOARD | Cardboard materials | Cardboard boxes, packaging |
| CLOTH | Textile and fabric items | Clothing, textiles |
| GLASS | Glass items | Bottles, jars, broken glass |
| METAL | Metal items | Cans, foil, metal objects |
| PAPER | Paper products | Documents, magazines, paper bags |
| PLASTIC | Plastic materials | Bottles, bags, containers |

### Disposal Categories (L2 Labels)

| Category (Chinese) | English | Mapped Materials |
|--------------------|---------|------------------|
| 可回收物 | Recycle | PLASTIC, PAPER, METAL, GLASS, CARDBOARD |
| 其他垃圾 | Trash | CLOTH |
| 有机垃圾 | Organic | BIODEGRADABLE |

View full mapping: `configs/category_mapping.json`

## Model Performance

Training setup:
- Dataset: 10,464 images (76% train, 14% valid, 10% test)
- Model: YOLOv8s
- Input Size: 640x640
- Batch Size: 32
- Training Time: ~3-5 hours (RTX 6000 Ada)

Expected performance metrics (with proper training):
- mAP@50: >0.80 (Target)
- mAP@50-95: >0.60 (Target)
- Precision: >0.75 (Target)
- Recall: >0.70 (Target)
- Inference Time: ~20-30ms per image (GPU)

## Training Improvements

This version includes optimized training configuration:
- **Increased learning rate**: 0.01 (from 0.001) for faster convergence
- **Enhanced data augmentation**:
  - Rotation, translation, scaling
  - Color augmentation (HSV)
  - Mixup and copy-paste
- **Better class balance**: Higher class loss weight (1.0)
- **Longer warmup**: 5 epochs for stable training
- **Smaller image size**: 640x640 (more efficient, less overfitting)

## Advanced Configuration

### Custom Training Parameters

Edit configuration in `scripts/train_yolov8.py`:

```python
config = {
    'model_size': 's',      # n, s, m, l, x
    'epochs': 150,
    'imgsz': 640,
    'batch': 32,
    'device': 0,
}
```

### Adjust Detection Thresholds

Modify inference parameters in `api/main.py`:

```python
results = model(img_array, conf=0.25, iou=0.45)
# conf: Confidence threshold (0–1)
# iou: IoU threshold for NMS (0–1)
```

### Custom Category Mapping

Edit `configs/category_mapping.json` to adjust L1-to-L2 mapping.

## Deployment Recommendations

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "api/main.py"]
```

### Production Environment

Use Gunicorn + Uvicorn workers:

```bash
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

## Common Issues

### 1. CUDA Out of Memory

If VRAM is insufficient, reduce batch size:

```python
config['batch'] = 16  # or smaller
```

### 2. Dataset Download Issues

- Ensure you have a Roboflow account
- Get your API key from: https://app.roboflow.com/settings/api
- Or download manually from Roboflow Universe

### 3. Slow Inference

Ensure:
- GPU is available (`torch.cuda.is_available()`)
- Model is moved to GPU
- Image preprocessing is optimized

## Dataset Comparison

**Previous (TACO)**:
- 616 images total
- 60 classes (7 empty, 28 with <10 samples)
- Severe class imbalance
- Poor performance: mAP@50 ~2%

**Current (Roboflow Garbage Classification)**:
- 10,464 images total (17x larger)
- 7 well-balanced classes
- Each class has 1000+ samples
- Expected performance: mAP@50 >80%

## License

This project is for learning and research purposes only.

The Garbage Classification Dataset is licensed under CC BY 4.0.
Source: https://universe.roboflow.com/material-identification/garbage-classification-3

## References

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Roboflow Universe - Garbage Classification](https://universe.roboflow.com/material-identification/garbage-classification-3)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Author

Project creation date: 2025-11-12
Updated: 2025-11-12 (Dataset migration from TACO to Roboflow)

---

**Note**: This project demonstrates a complete workflow from data preparation, model training, to API deployment using state-of-the-art object detection techniques.
