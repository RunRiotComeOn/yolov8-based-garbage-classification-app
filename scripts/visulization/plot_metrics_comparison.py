#!/usr/bin/env python3
"""
对比YOLOv8s和YOLOv8m的评估指标(Precision, Recall, mAP)变化趋势
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

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
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('YOLOv8s vs YOLOv8m - Metrics Comparison', fontsize=16, fontweight='bold')

# 指标列表
metrics = [
    ('metrics/precision(B)', 'Precision'),
    ('metrics/recall(B)', 'Recall'),
    ('metrics/mAP50(B)', 'mAP@0.5'),
    ('metrics/mAP50-95(B)', 'mAP@0.5:0.95')
]

for idx, (metric_name, title) in enumerate(metrics):
    ax = axes[idx // 2, idx % 2]

    # 过滤掉无穷值和NaN
    df_s_clean = df_s[df_s[metric_name].notna() & ~df_s[metric_name].isin([float('inf'), float('-inf')])]
    df_m_clean = df_m[df_m[metric_name].notna() & ~df_m[metric_name].isin([float('inf'), float('-inf')])]

    ax.plot(df_s_clean['epoch'], df_s_clean[metric_name], label='YOLOv8s', linewidth=2, alpha=0.8, marker='o', markersize=3, markevery=10)
    ax.plot(df_m_clean['epoch'], df_m_clean[metric_name], label='YOLOv8m', linewidth=2, alpha=0.8, marker='s', markersize=3, markevery=10)

    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # 添加最终值标注
    if len(df_s_clean) > 0:
        final_s = df_s_clean[metric_name].iloc[-1]
        ax.text(0.02, 0.98, f'YOLOv8s final: {final_s:.4f}',
                transform=ax.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    if len(df_m_clean) > 0:
        final_m = df_m_clean[metric_name].iloc[-1]
        ax.text(0.02, 0.88, f'YOLOv8m final: {final_m:.4f}',
                transform=ax.transAxes, fontsize=9, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

plt.tight_layout()
output_path = '/nas03/yixuh/garbage-classification/scripts/visulization/metrics_comparison.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"Metrics comparison plot saved to: {output_path}")
plt.close()
