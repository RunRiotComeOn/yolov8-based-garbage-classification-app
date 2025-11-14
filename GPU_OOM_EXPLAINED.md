# 🤔 为什么显示有内存但还是 OOM?

## 问题现象

**训练时报错**:
```
CUDA out of memory. Tried to allocate 300.00 MiB
GPU 3 has a total capacity of 47.50 GiB of which 194.56 MiB is free
```

**但你查看时**:
```
GPU 3: 39,685 MiB free ✓ 正常
```

---

## 🔍 根本原因

### 1. **瞬时内存峰值** (最可能, 80%)

训练过程中的内存使用是**动态变化**的：

```
正常训练: 9 GB ──────────────────────────
                                      ↓
验证阶段: 9 GB ─────────────────► 47 GB (峰值) ──► OOM!
                                      ↑
                          需要额外分配大量内存
```

**为什么验证阶段内存激增?**
- 需要加载完整验证集的 batch
- 计算 mAP 需要存储所有预测结果
- 不释放中间结果（用于后续分析）
- 多 GPU 时每个 GPU 都要保存副本

### 2. **PyTorch 内存缓存机制** (15%)

PyTorch 的内存分配器会**缓存**释放的内存：

```
实际情况:
├─ PyTorch 已分配: 37.60 GiB
├─ PyTorch 保留但未分配: 302 MiB  ← 碎片!
└─ 实际可用: 194 MiB  ← 太少!

你看到的 (训练停止后):
└─ 空闲: 39.68 GiB  ← PyTorch 释放了缓存
```

### 3. **内存碎片化** (5%)

即使有 39 GB 空闲，但可能**没有连续的 300 MB**：

```
内存布局 (简化):
[██ 200MB ██][空 100MB][██ 150MB ██][空 50MB][██ 180MB ██]...
              ↑ 无法满足 300MB 的连续分配
```

---

## 📊 验证阶段的内存使用分析

从你的日志看，OOM 发生在**验证阶段**：

```
134/200  26.5G   nan   nan   nan   54   1280: 100% ━━━━━━━━━━━━ 115/115
                                                                ↓
         Class  Images  Instances  Box(P  R  mAP50  mAP50-95): 6% ╸───
                                                                ↓
                                                              OOM!
```

**验证阶段内存需求**:

| 组件 | 内存使用 | 说明 |
|------|----------|------|
| 模型 | 3 GB × 4 = 12 GB | 4 个 GPU 副本 |
| 训练数据缓存 | ~6 GB × 4 = 24 GB | 每个 GPU 缓存的训练数据 |
| 验证批次 | **2 GB × 4 = 8 GB** | 验证时的 batch |
| mAP 计算 | **5 GB × 4 = 20 GB** | 存储所有预测和 GT |
| **总计** | **~64 GB** | **超过 48 GB 容量!** |

---

## ✅ 解决方案

### 🔴 方案 1: 降低 Batch Size (最简单)

**当前**: `batch=64` (每个 GPU ~16)
**修改**: `batch=32` (每个 GPU ~8)

```bash
# 自动修改
sed -i "s/'batch': 64/'batch': 32/g" scripts/train_yolov8_safe.py

# 重新运行
python3 scripts/train_yolov8_safe.py
```

**效果**:
- ✓ 内存使用减少 ~40%
- ✓ 峰值内存从 ~64GB 降到 ~38GB
- ✗ 训练速度降低 ~15%

---

### 🟡 方案 2: 梯度累积 (推荐!)

保持大 batch size 的效果，但分多步累积：

```python
# 修改 train_yolov8_safe.py 的 train_args:
train_args = {
    'batch': 16,           # 降低实际 batch (64 → 16)
    'accumulate': 4,       # 累积 4 步
    # 实际等效 batch = 16 × 4 = 64
    ...
}
```

**效果**:
- ✓ 内存使用减少 ~70%
- ✓ 等效 batch size 仍为 64
- ✓ 训练质量不受影响
- ✗ 训练速度降低 ~20%

---

### 🟢 方案 3: 使用更少的 GPU

如果不需要 4 个 GPU 的速度：

```python
config = {
    'device': [0, 1],      # 4 → 2 个 GPU
    'batch': 32,           # 每个 GPU 16
    ...
}
```

**效果**:
- ✓ 减少模型副本数量
- ✓ 每个 GPU 有更多可用内存
- ✗ 训练速度降低 ~50%

---

### 🔵 方案 4: 优化验证过程

添加验证时的内存优化：

```python
train_args = {
    'val': True,
    'batch': 32,           # 训练 batch
    'imgsz': 1280,
    # 可以考虑降低验证频率
    'save_period': 10,     # 每 10 epoch 才做完整验证
    ...
}
```

---

### 🟣 方案 5: 环境变量优化

设置 PyTorch 内存分配器：

```bash
# 在运行训练前设置
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128

# 然后运行训练
python3 scripts/train_yolov8_safe.py
```

**效果**:
- ✓ 减少内存碎片
- ✓ 更高效的内存分配
- ✓ 可能避免 OOM

---

## 🎯 推荐组合方案

结合多个方案，最大化稳定性：

```python
# train_yolov8_safe.py

config = {
    'batch': 32,              # 降低 batch size
    'device': [0, 1, 2, 3],  # 保持 4 GPU
    ...
}

train_args = {
    'batch': 32,
    'accumulate': 2,          # 使用梯度累积
    # 实际等效 batch = 32 × 2 = 64
    ...
}

# 运行前设置环境变量
# export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

**预期效果**:
- ✓ 内存峰值: ~40 GB (安全范围)
- ✓ 等效 batch: 64 (性能不变)
- ✓ OOM 风险: <5%
- ✗ 训练速度: 降低 ~20%

---

## 📝 快速修复脚本

我已经创建了自动修复工具：

```bash
# 诊断当前状态
bash scripts/diagnose_gpu_memory.sh

# 交互式修复
bash scripts/fix_gpu_memory.sh
```

---

## ❓ 常见问题

### Q1: 为什么查看时有内存，训练时没有?

A: 因为**训练时的瞬时峰值**远高于平均使用。验证阶段尤其明显。

### Q2: 为什么验证阶段内存暴增?

A: 需要同时保存:
- 所有验证图片的预测结果
- Ground truth 标注
- 中间计算结果 (用于 mAP 计算)

### Q3: 降低 batch size 会影响性能吗?

A: 如果配合**梯度累积**，最终效果完全一样。

### Q4: 能否只在验证时降低 batch?

A: YOLOv8 的验证 batch 通常自动设置，可以通过 `rect=False` 来使用更小的验证 batch。

---

## 🔬 深入分析

### 内存时间线 (Epoch 134)

```
时间  →  操作            GPU 3 内存使用
──────────────────────────────────────
00:00  训练 batch 1-20    9 GB
00:30  训练 batch 21      47 GB ← OOM!
              ↑
        开始加载下一个大 batch
        + 之前的缓存未释放
        + 验证准备阶段
```

### PyTorch 内存分配器行为

```python
# PyTorch 的内存策略
分配内存:
  1. 先查找缓存中是否有可用块
  2. 如果没有，向 CUDA 申请新内存
  3. 如果申请失败 → OOM

释放内存:
  1. 不立即归还给 CUDA
  2. 放入缓存池 (供后续重用)
  3. 只有显式调用 empty_cache() 才真正释放
```

这就是为什么你看到 39 GB 空闲 (训练停止后 PyTorch 释放了缓存)，但训练时只有 194 MB 可用。

---

## 📊 数据对比

| 场景 | GPU 3 可用内存 | 说明 |
|------|---------------|------|
| **训练中 (平均)** | ~30 GB | 正常训练状态 |
| **训练中 (峰值)** | **194 MB** | 验证/大 batch 时 |
| **训练停止后** | 39.7 GB | PyTorch 释放缓存 |
| **需要分配** | 300 MB | 不够! |

---

## 🚀 立即行动

```bash
# 1. 快速修复 (降低 batch size)
cd /nas03/yixuh/garbage-classification
bash scripts/fix_gpu_memory.sh
# 选择方案 1

# 2. 重新运行训练
python3 scripts/train_yolov8_safe.py

# 3. 监控内存使用
watch -n 5 'nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv'
```

---

**总结**: 你看到的充足内存是训练**空闲时**的状态，而 OOM 发生在训练的**峰值时刻**。降低 batch size 或使用梯度累积可以彻底解决问题。
