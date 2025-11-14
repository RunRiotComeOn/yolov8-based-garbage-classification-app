# 🚨 训练出现 NaN 问题 - 紧急处理指南

## 问题描述
在 epoch 134/200 时，训练突然出现 NaN (Not a Number)：
- 第 1-20 个 batch: Loss 正常 (1.88 左右)
- 第 21 个 batch 开始: 所有 loss 变成 nan
- Checkpoint 已被污染，无法恢复

```
134/200      24.6G       1.88       4.06      1.659        316       1280
134/200      24.6G        nan        nan        nan        294       1280  ← 从这里开始出问题
```

---

## 🔍 根本原因分析

### 最可能的原因（按概率排序）：

#### 1. 🔴 **梯度爆炸 (Gradient Explosion)** - 概率 70%
**症状**:
- Loss 突然从正常值变成 NaN
- 发生在高分辨率训练 (1280) 时
- GPU 内存使用从 24.6G 增加

**原因**:
- 分辨率从 640 → 1280，梯度幅度增加 4 倍
- 学习率可能过高 (lr0=0.01 对 1280 分辨率偏高)
- 混合精度训练 (AMP) 可能导致数值不稳定

#### 2. 🟡 **学习率过高** - 概率 15%
- lr0=0.01 对于 imgsz=1280 可能太大
- 在 epoch 134，学习率约为 0.01 * (1-134/200) = 0.0033，仍然较高

#### 3. 🟡 **数据异常** - 概率 10%
- 某些训练样本可能包含异常值
- 标注框可能超出图像边界
- 图像预处理出现问题

#### 4. 🟢 **混合精度训练 (AMP) 数值溢出** - 概率 5%
- FP16 表示范围有限，可能溢出

---

## ⚡ 紧急修复方案

### 方案 A: 从干净的 checkpoint 恢复（推荐）

#### Step 1: 找到最后一个干净的 checkpoint
```bash
cd /nas03/yixuh/garbage-classification/models/garbage_yolov8m_v2/weights

# 检查 epoch130.pt 是否存在（每10个epoch保存一次）
ls -lh epoch*.pt

# 如果有 epoch130.pt，使用它
# 如果没有，检查 best.pt
```

#### Step 2: 删除损坏的 checkpoint
```bash
# 备份（以防万一）
mkdir -p corrupted_backup
mv last.pt corrupted_backup/last_epoch134_corrupted.pt

# 复制干净的 checkpoint
cp epoch130.pt last.pt
# 或者
cp best.pt last.pt
```

#### Step 3: 修改训练配置，降低学习率
在 `train_yolov8.py` 中修改：
```python
train_args = {
    'lr0': 0.005,          # ← 降低初始学习率 (0.01 → 0.005)
    'lrf': 0.0001,         # ← 降低最终学习率
    'warmup_epochs': 3.0,  # ← 减少 warmup
    'box': 8.0,            # ← 降低 box loss weight (10.0 → 8.0)
    'cls': 1.5,
    'amp': False,          # ← 暂时禁用混合精度训练
    'optimizer': 'SGD',    # ← 尝试 SGD (比 AdamW 更稳定)
    'momentum': 0.937,
    'weight_decay': 0.0005,
    # ... 其他参数
}
```

#### Step 4: 从干净的 checkpoint 继续训练
```python
config = {
    'resume': True,  # ← 设置为 True
    # ... 其他配置
}
```

---

### 方案 B: 重新开始训练（如果没有干净的 checkpoint）

#### 调整后的训练配置
```python
train_args = {
    # === 关键修改 ===
    'lr0': 0.003,              # 大幅降低学习率 (1280 分辨率需要更低 LR)
    'lrf': 0.00001,            # 最终学习率
    'warmup_epochs': 5.0,      # 增加 warmup，让训练更稳定
    'amp': False,              # 禁用混合精度（牺牲速度换稳定性）
    'optimizer': 'SGD',        # SGD 比 AdamW 更稳定

    # === 降低 loss weights ===
    'box': 7.5,                # 恢复默认值
    'cls': 1.0,                # 恢复默认值
    'dfl': 1.5,                # 保持不变

    # === 减少数据增强强度 ===
    'hsv_h': 0.015,            # 降低 (0.05 → 0.015)
    'hsv_s': 0.7,              # 降低 (1.0 → 0.7)
    'hsv_v': 0.4,              # 降低 (0.8 → 0.4)
    'mixup': 0.0,              # 暂时禁用
    'copy_paste': 0.0,         # 暂时禁用
    'mosaic': 0.9,             # 降低

    # === 其他稳定性设置 ===
    'batch': 64,               # 降低 batch size (128 → 64)
    'close_mosaic': 50,        # 更早关闭 mosaic（在最后50个epoch）
}
```

---

## 🛡️ 预防措施（长期解决方案）

### 1. **梯度裁剪** (推荐!)
```python
# 在 train_yolov8.py 中无法直接设置，但可以通过修改 ultralytics 源码
# 或者创建自定义训练循环

# 临时解决：降低学习率来间接控制梯度
'lr0': 0.002,  # 非常保守的学习率
```

### 2. **渐进式分辨率训练**
```python
# 方案：先用 640 训练，再用 1280 fine-tune
# Phase 1: 训练 150 epochs with imgsz=640
# Phase 2: 继续训练 50 epochs with imgsz=1280, lr0=0.001
```

### 3. **监控和早期停止**
创建一个监控脚本：

```python
# monitor_training.py
import pandas as pd
import time

def check_for_nan(csv_path):
    """检查训练是否出现 NaN"""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    # 检查最新一行
    last_row = df.iloc[-1]

    if pd.isna(last_row['train/box_loss']) or \
       pd.isna(last_row['train/cls_loss']) or \
       pd.isna(last_row['train/dfl_loss']):
        print("⚠️  WARNING: NaN detected!")
        print(f"Epoch: {last_row['epoch']}")
        print("Training should be stopped immediately!")
        return True

    return False

# 每分钟检查一次
while True:
    if check_for_nan('models/garbage_yolov8m_v2/results.csv'):
        # 发送警报或自动停止训练
        break
    time.sleep(60)
```

### 4. **使用更保守的优化器设置**
```python
'optimizer': 'SGD',           # 而不是 AdamW
'momentum': 0.9,              # 标准动量
'weight_decay': 0.0001,       # 更小的权重衰减
'nesterov': True,             # Nesterov 动量（如果支持）
```

---

## 📋 推荐的完整配置（NaN-safe）

```python
# train_yolov8_safe.py
config = {
    'model_size': 'm',        # 先用 m，稳定后再试 l
    'epochs': 200,
    'imgsz': 1280,
    'batch': 64,              # 降低 batch size
    'device': [0, 1, 2, 3],
    'project': 'models',
    'name': 'garbage_yolov8m_v3_safe',
    'resume': False
}

train_args = {
    # ============= 稳定性优先设置 =============
    'lr0': 0.003,             # 🔴 关键：降低学习率
    'lrf': 0.00001,
    'optimizer': 'SGD',       # 🔴 关键：使用 SGD
    'momentum': 0.937,
    'weight_decay': 0.0005,
    'warmup_epochs': 10.0,    # 🔴 关键：更长的 warmup

    'amp': False,             # 🔴 禁用 AMP，避免 FP16 溢出

    'box': 7.5,               # 标准 loss weights
    'cls': 1.0,
    'dfl': 1.5,

    # ============= 适度的数据增强 =============
    'hsv_h': 0.015,
    'hsv_s': 0.7,
    'hsv_v': 0.4,
    'degrees': 10.0,          # 降低旋转
    'translate': 0.1,         # 降低平移
    'scale': 0.5,             # 降低缩放
    'shear': 2.0,             # 降低剪切
    'perspective': 0.0,       # 禁用透视
    'flipud': 0.0,            # 禁用上下翻转
    'fliplr': 0.5,            # 保留左右翻转
    'mosaic': 0.8,
    'mixup': 0.0,             # 禁用 mixup
    'copy_paste': 0.0,        # 禁用 copy-paste

    'close_mosaic': 50,       # 最后 50 epoch 关闭 mosaic
    'patience': 100,
    'save_period': 5,         # 🔴 更频繁地保存 (每 5 个 epoch)
}
```

---

## 🔬 调试和诊断

### 检查数据集
```bash
# 查找可能的异常标注
cd /nas03/yixuh/garbage-classification

python3 << 'EOF'
import os
import glob

def check_labels(label_dir):
    """检查标注文件是否有异常"""
    label_files = glob.glob(f"{label_dir}/**/*.txt", recursive=True)

    issues = []
    for label_file in label_files:
        with open(label_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split()
                if len(parts) == 0:
                    continue

                try:
                    cls = int(parts[0])
                    x, y, w, h = map(float, parts[1:5])

                    # 检查值是否在合理范围内
                    if not (0 <= x <= 1 and 0 <= y <= 1 and
                            0 <= w <= 1 and 0 <= h <= 1):
                        issues.append(f"{label_file}:{line_num} - 坐标超出范围: {line.strip()}")

                    if cls < 0 or cls > 5:  # 6 个类别 (0-5)
                        issues.append(f"{label_file}:{line_num} - 类别异常: {cls}")

                except ValueError as e:
                    issues.append(f"{label_file}:{line_num} - 格式错误: {line.strip()}")

    return issues

# 检查训练集标注
issues = check_labels('data/processed/labels/train')
if issues:
    print("发现以下标注问题：")
    for issue in issues[:20]:  # 只显示前 20 个
        print(issue)
else:
    print("✓ 标注检查通过")
EOF
```

### 查看损坏的 checkpoint
```python
# check_checkpoint.py
import torch

checkpoint_path = '/nas03/yixuh/garbage-classification/models/garbage_yolov8m_v2/weights/last.pt'

try:
    ckpt = torch.load(checkpoint_path, map_location='cpu')

    # 检查权重是否包含 NaN/Inf
    has_nan = False
    has_inf = False

    if 'model' in ckpt:
        for name, param in ckpt['model'].state_dict().items():
            if torch.isnan(param).any():
                print(f"❌ NaN found in: {name}")
                has_nan = True
            if torch.isinf(param).any():
                print(f"❌ Inf found in: {name}")
                has_inf = True

    if not has_nan and not has_inf:
        print("✓ Checkpoint is clean")
    else:
        print(f"\n⚠️  Checkpoint is corrupted!")
        print(f"   NaN layers: {has_nan}")
        print(f"   Inf layers: {has_inf}")

except Exception as e:
    print(f"Error loading checkpoint: {e}")
```

---

## ⚡ 立即执行（分步指南）

### Step 1: 停止当前训练
```bash
# 找到训练进程
ps aux | grep train_yolov8.py

# 杀掉进程
kill -9 <PID>
```

### Step 2: 检查可用的 checkpoint
```bash
cd /nas03/yixuh/garbage-classification/models/garbage_yolov8m_v2/weights
ls -lht epoch*.pt | head -5
```

### Step 3: 创建安全训练配置
```bash
# 复制训练脚本
cp scripts/train_yolov8.py scripts/train_yolov8_safe.py
```

编辑 `train_yolov8_safe.py`，应用上述推荐配置。

### Step 4: 从干净的 checkpoint 重启
```bash
# 如果有 epoch130.pt
cp epoch130.pt last.pt

# 修改 config
resume: True
```

### Step 5: 运行训练并监控
```bash
# 在一个终端运行训练
python3 scripts/train_yolov8_safe.py

# 在另一个终端监控
watch -n 10 'tail -20 models/garbage_yolov8m_v3_safe/results.csv'
```

---

## 🎯 关键要点

1. **立即降低学习率**: 0.01 → 0.003
2. **禁用混合精度**: amp: False
3. **使用 SGD**: 比 AdamW 更稳定
4. **增加 warmup**: 让训练开始更平稳
5. **更频繁保存**: save_period: 5
6. **减少数据增强**: 避免极端样本

**预期效果**:
- 训练速度会慢 20-30%（禁用 AMP）
- 但会极大提高稳定性
- 应该能顺利完成 200 epochs

---

*紧急情况下，如需帮助请查看 `/scripts/visulization/URGENT_NAN_ISSUE_GUIDE.md`*
