# 训练结果可视化脚本

这个目录包含了用于可视化YOLOv8训练结果的Python脚本。

## 可用脚本

### 1. `plot_loss_comparison.py`
**功能**: 对比YOLOv8s和YOLOv8m两个模型的训练和验证损失
- 训练损失: Box Loss, Classification Loss, DFL Loss
- 验证损失: Box Loss, Classification Loss, DFL Loss
- **输出**: `loss_comparison.png`

### 2. `plot_metrics_comparison.py`
**功能**: 对比两个模型的评估指标
- Precision (精确度)
- Recall (召回率)
- mAP@0.5
- mAP@0.5:0.95
- 显示最终值
- **输出**: `metrics_comparison.png`

### 3. `plot_training_overview.py`
**功能**: 为每个模型生成详细的训练过程概览
- 训练损失趋势
- 验证损失趋势
- 总损失对比
- Precision & Recall
- mAP指标
- 学习率变化
- 训练统计摘要
- **输出**:
  - `yolov8s_training_overview.png`
  - `yolov8m_training_overview.png`

### 4. `plot_all.py`
**功能**: 一键运行所有可视化脚本
```bash
python3 plot_all.py
```

## 使用方法

### 运行所有可视化
```bash
cd /nas03/yixuh/garbage-classification/scripts/visulization
python3 plot_all.py
```

### 运行单个脚本
```bash
python3 plot_loss_comparison.py       # 只生成损失对比图
python3 plot_metrics_comparison.py    # 只生成指标对比图
python3 plot_training_overview.py     # 只生成训练概览图
```

## 输出文件

所有生成的图表都保存在当前目录下:
- `loss_comparison.png` - 损失对比图
- `metrics_comparison.png` - 评估指标对比图
- `yolov8s_training_overview.png` - YOLOv8s详细概览
- `yolov8m_training_overview.png` - YOLOv8m详细概览

## 数据源

脚本从以下CSV文件读取训练结果:
- `/nas03/yixuh/garbage-classification/models/garbage_yolov8s/results.csv`
- `/nas03/yixuh/garbage-classification/models/garbage_yolov8m/results.csv`

## 依赖库

- pandas
- matplotlib
- numpy (可选)

## 注意事项

- 脚本会自动过滤掉无穷值(inf)和NaN值
- 使用非交互式后端(Agg),适合在无显示器的服务器上运行
- 所有图表分辨率为150 DPI,确保清晰度
