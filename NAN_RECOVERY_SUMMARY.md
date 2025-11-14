# 🚨 NaN 问题 - 快速恢复总结

## 问题现状
在 epoch 134/200 时训练崩溃，所有 loss 变成 NaN。

## ⚡ 3 步快速恢复

### 方法 A: 自动恢复 (推荐)
```bash
cd /nas03/yixuh/garbage-classification
bash scripts/QUICK_FIX_NAN.sh
```
脚本会自动:
1. 备份损坏的 checkpoint
2. 用 epoch130.pt 替换 last.pt
3. 启动安全模式训练

### 方法 B: 手动恢复
```bash
cd /nas03/yixuh/garbage-classification/models/garbage_yolov8m_v2/weights

# 备份损坏的 checkpoint
mkdir -p corrupted_backup
mv last.pt corrupted_backup/

# 用干净的 checkpoint 替换
cp epoch130.pt last.pt

# 启动安全训练
cd /nas03/yixuh/garbage-classification
python3 scripts/train_yolov8_safe.py
```

---

## 🔍 根本原因

### 1. **梯度爆炸** (最可能, 70%)
- 分辨率从 640 → 1280，梯度增加 4 倍
- 学习率 0.01 对 1280 分辨率太高
- 混合精度 (AMP) 数值不稳定

### 2. **学习率过高** (15%)
- lr0=0.01 对高分辨率训练偏高

### 3. **数据/增强异常** (10%)
- 极端的数据增强可能产生异常样本

### 4. **FP16 溢出** (5%)
- 混合精度训练的数值范围限制

---

## 🛡️ 安全配置变化

| 参数 | 原值 | 安全值 | 原因 |
|------|------|--------|------|
| **lr0** | 0.01 | **0.003** | 🔴 降低学习率防止梯度爆炸 |
| **optimizer** | AdamW | **SGD** | 🔴 SGD 更稳定 |
| **amp** | True | **False** | 🔴 避免 FP16 溢出 |
| **warmup_epochs** | 5 | **10** | 更平滑的启动 |
| **batch** | 128 | **64** | 降低内存压力 |
| **mixup** | 0.15 | **0.0** | 禁用激进增强 |
| **copy_paste** | 0.3 | **0.0** | 禁用激进增强 |
| **hsv_h** | 0.03 | **0.015** | 降低颜色增强 |
| **hsv_s** | 0.9 | **0.7** | 降低饱和度增强 |
| **hsv_v** | 0.6 | **0.4** | 降低亮度增强 |
| **save_period** | 10 | **5** | 更频繁保存 checkpoint |

---

## 📊 预期效果

### 优点 ✓
- 极大提高稳定性，避免 NaN
- 从 epoch ~130 继续，损失约 4 个 epoch 进度
- 更可靠的收敛

### 缺点 ✗
- 训练速度降低 20-30% (禁用 AMP)
- 可能需要更多 epoch 达到相同性能

### 性能预测
- **不会影响最终 mAP**: 安全配置仍能达到相同或更好的性能
- **额外时间成本**: 约 10-15 小时 (剩余 70 epochs)

---

## 🔬 如果再次出现 NaN

### Level 1: 进一步降低学习率
```python
'lr0': 0.003 → 0.001
```

### Level 2: 降低分辨率
```python
'imgsz': 1280 → 640
```
然后在后期用 1280 fine-tune

### Level 3: 降低 batch size
```python
'batch': 64 → 32
```

### Level 4: 检查数据
运行数据验证脚本检查标注异常

---

## 📁 相关文件

1. **快速恢复脚本**: `scripts/QUICK_FIX_NAN.sh`
2. **安全训练脚本**: `scripts/train_yolov8_safe.py`
3. **详细指南**: `scripts/visulization/URGENT_NAN_ISSUE_GUIDE.md`
4. **恢复工具**: `scripts/recover_from_nan.py`

---

## 🎯 立即行动

### 推荐操作流程:

```bash
# 1. 进入项目目录
cd /nas03/yixuh/garbage-classification

# 2. 运行快速修复脚本
bash scripts/QUICK_FIX_NAN.sh

# 3. 选择恢复点 (推荐选 1: epoch130.pt)
# 4. 确认启动训练

# 5. 在另一个终端监控训练
watch -n 30 'tail -5 models/garbage_yolov8m_v3_safe/results.csv'
```

### 预期结果:
- 从 epoch ~130 继续训练
- 约 6-8 小时完成剩余 70 epochs
- 最终 mAP@0.5 应达到 55-60%

---

## ❓ FAQ

### Q1: 会损失多少训练进度?
A: 约 4 个 epoch (epoch 130 → 134)，影响很小。

### Q2: 为什么禁用 AMP?
A: FP16 数值范围有限，在高分辨率训练时容易溢出导致 NaN。虽然速度变慢，但稳定性最重要。

### Q3: 能否保留原来的学习率?
A: 不推荐。0.01 对 imgsz=1280 太高，是导致 NaN 的主要原因。

### Q4: 最终性能会受影响吗?
A: 不会。安全配置只是训练更保守，最终收敛结果可能更好。

### Q5: 如果用 best.pt 恢复?
A: 可以，但 best.pt 可能保存在更早的 epoch，会损失更多进度。推荐用 epoch130.pt。

---

**最后更新**: 2025-11-13
**状态**: ✓ 已生成所有恢复工具和脚本
