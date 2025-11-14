#!/usr/bin/env python3
"""
对比YOLOv8s和YOLOv8m的训练和验证损失变化趋势
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
yolov8s_path = '/nas03/yixuh/garbage-classification/models/garbage_yolov8s/results.csv'
yolov8m_path = '/nas03/yixuh/garbage-classification/models/garbage_yolov8m/results.csv'

df_s = pd.read_csv(yolov8s_path)
df_m = pd.read_csv(yolov8m_path)

# 去除空格
df_s.columns = df_s.columns.str.strip()
df_m.columns = df_m.columns.str.strip()

# 创建图表
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('YOLOv8s vs YOLOv8m - Loss Comparison', fontsize=16, fontweight='bold')

# 训练损失对比
losses = [
    ('train/box_loss', 'Training Box Loss'),
    ('train/cls_loss', 'Training Classification Loss'),
    ('train/dfl_loss', 'Training DFL Loss')
]

for idx, (loss_name, title) in enumerate(losses):
    ax = axes[0, idx]
    ax.plot(df_s['epoch'], df_s[loss_name], label='YOLOv8s', linewidth=2, alpha=0.8)
    ax.plot(df_m['epoch'], df_m[loss_name], label='YOLOv8m', linewidth=2, alpha=0.8)
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('Loss', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

# 验证损失对比
val_losses = [
    ('val/box_loss', 'Validation Box Loss'),
    ('val/cls_loss', 'Validation Classification Loss'),
    ('val/dfl_loss', 'Validation DFL Loss')
]

for idx, (loss_name, title) in enumerate(val_losses):
    ax = axes[1, idx]
    # 过滤掉无穷值和NaN
    df_s_clean = df_s[df_s[loss_name].notna() & ~df_s[loss_name].isin([float('inf'), float('-inf')])]
    df_m_clean = df_m[df_m[loss_name].notna() & ~df_m[loss_name].isin([float('inf'), float('-inf')])]

    ax.plot(df_s_clean['epoch'], df_s_clean[loss_name], label='YOLOv8s', linewidth=2, alpha=0.8)
    ax.plot(df_m_clean['epoch'], df_m_clean[loss_name], label='YOLOv8m', linewidth=2, alpha=0.8)
    ax.set_xlabel('Epoch', fontsize=11)
    ax.set_ylabel('Loss', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
output_path = '/nas03/yixuh/garbage-classification/scripts/visulization/loss_comparison.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"Loss comparison plot saved to: {output_path}")
plt.close()
