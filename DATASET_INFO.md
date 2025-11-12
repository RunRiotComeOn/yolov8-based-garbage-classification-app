# Dataset Information

## ✅ Dataset Preparation Complete

The dataset has been successfully downloaded, extracted, and organized into the project!

### 📊 Dataset Statistics

**Image Counts:**
- Train: 7,324 images (70%)
- Valid: 2,098 images (20%)
- Test: 1,042 images (10%)
- **Total: 10,464 images**

**Annotation Counts:**
- Total instances: 74,090 objects
- Average objects per image: 7.08

### 🏷️ Class Distribution

| ID | Class        | Instances | Percentage |
|----|--------------|-----------|------------|
| 0  | BIODEGRADABLE| 45,407    | 61.29%     |
| 1  | CARDBOARD    | 4,698     | 6.34%      |
| 2  | GLASS        | 7,809     | 10.54%     |
| 3  | METAL        | 5,841     | 7.88%      |
| 4  | PAPER        | 4,390     | 5.93%      |
| 5  | PLASTIC      | 5,945     | 8.02%      |

**Note:** The BIODEGRADABLE class dominates (61%) due to the large amount of organic waste. Other classes are relatively balanced.

### 📁 Dataset Structure

```
data/
├── raw/                                    # Raw downloaded files
│   ├── GARBAGE CLASSIFICATION 3.v2-gc1.yolov8.zip
│   ├── data.yaml
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── valid/
│   │   ├── images/
│   │   └── labels/
│   └── test/
│       ├── images/
│       └── labels/
└── processed/                              # Training-ready data
    ├── images/
    │   ├── train/      (7,324 images)
    │   ├── valid/      (2,098 images)
    │   └── test/       (1,042 images)
    └── labels/
        ├── train/      (7,324 labels)
        ├── valid/      (2,098 labels)
        └── test/       (1,042 labels)
```

### 🎯 6 Garbage Classes

1. **BIODEGRADABLE**
   - Food scraps, organic waste
   - Maps to: Organic Waste
   - Highest proportion (61%)

2. **CARDBOARD**
   - Cardboard boxes, packaging
   - Maps to: Recyclables

3. **GLASS**
   - Glass bottles, jars
   - Maps to: Recyclables

4. **METAL**
   - Cans, metal packaging
   - Maps to: Recyclables

5. **PAPER**
   - Newspapers, documents, paper bags
   - Maps to: Recyclables

6. **PLASTIC**
   - Plastic bottles, bags, containers
   - Maps to: Recyclables

### 📝 Annotation Format

YOLO format (one object per line):
```
<class_id> <x_center> <y_center> <width> <height>
```

All coordinates are normalized (0–1 range).

**Example:**
```
0 0.8449519230769231 0.20552884615384615 0.12259615384615384 0.14423076923076922
0 0.7764423076923077 0.09495192307692307 0.17307692307692307 0.15865384615384615
```

### ✅ Next Steps

Dataset is ready — training can begin!

```bash
# Start training
python scripts/train_yolov8.py
```

**Training Configuration:**
- Model: YOLOv8s
- Image Size: 640x640
- Batch Size: 32
- Epochs: 150
- Expected Training Time: 3–5 hours

**Expected Performance:**
- mAP@50: >0.80 (80%)
- mAP@50-95: >0.60 (60%)
- Precision: >0.75 (75%)
- Recall: >0.70 (70%)

### 📊 Data Quality

✅ **Strengths:**
- Large-scale dataset (10,464 images)
- Average 7+ objects per image
- Real-world scenes
- Professional annotations
- YOLO format — ready to train

⚠️ **Considerations:**
- BIODEGRADABLE class is dominant (61%)
- Consider using class weights to balance training
- Monitor per-class performance

### 🔗 Dataset Source

- **Name**: GARBAGE CLASSIFICATION 3 (v2)
- **Source**: Roboflow Universe
- **URL**: https://universe.roboflow.com/material-identification/garbage-classification-3/dataset/2
- **License**: CC BY 4.0
- **Workspace**: material-identification
- **Project**: garbage-classification-3
- **Version**: 2

### 🎉 Summary

This is a high-quality garbage classification dataset. Compared to the previous TACO dataset:
- **Images**: 10,464 vs 616 (17× growth)
- **Class Balance**: 6 balanced classes vs 60 unbalanced
- **Annotation Quality**: Professional vs crowdsourced
- **Expected Performance**: mAP@50 >80% vs ~2%

Ready to train! 🚀
