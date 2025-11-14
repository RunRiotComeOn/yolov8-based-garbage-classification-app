#!/usr/bin/env python3
"""
综合展示单个模型的训练过程(Loss, Metrics, Learning Rate)
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import sys

matplotlib.use('Agg')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def plot_model_overview(csv_path, model_name, output_path):
    """绘制单个模型的训练概览"""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    fig.suptitle(f'{model_name} Training Overview', fontsize=16, fontweight='bold')

    # 1. 训练损失 (左上)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(df['epoch'], df['train/box_loss'], label='Box Loss', linewidth=2)
    ax1.plot(df['epoch'], df['train/cls_loss'], label='Cls Loss', linewidth=2)
    ax1.plot(df['epoch'], df['train/dfl_loss'], label='DFL Loss', linewidth=2)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Losses', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. 验证损失 (中上)
    ax2 = fig.add_subplot(gs[0, 1])
    df_clean = df[df['val/box_loss'].notna() & ~df['val/box_loss'].isin([float('inf'), float('-inf')])]
    ax2.plot(df_clean['epoch'], df_clean['val/box_loss'], label='Box Loss', linewidth=2)

    df_clean_cls = df[df['val/cls_loss'].notna() & ~df['val/cls_loss'].isin([float('inf'), float('-inf')])]
    ax2.plot(df_clean_cls['epoch'], df_clean_cls['val/cls_loss'], label='Cls Loss', linewidth=2)

    df_clean_dfl = df[df['val/dfl_loss'].notna() & ~df['val/dfl_loss'].isin([float('inf'), float('-inf')])]
    ax2.plot(df_clean_dfl['epoch'], df_clean_dfl['val/dfl_loss'], label='DFL Loss', linewidth=2)

    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.set_title('Validation Losses', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. 总损失对比 (右上)
    ax3 = fig.add_subplot(gs[0, 2])
    df['train_total_loss'] = df['train/box_loss'] + df['train/cls_loss'] + df['train/dfl_loss']
    df['val_total_loss'] = df['val/box_loss'] + df['val/cls_loss'] + df['val/dfl_loss']

    ax3.plot(df['epoch'], df['train_total_loss'], label='Train Total Loss', linewidth=2)
    df_val_clean = df[df['val_total_loss'].notna() & ~df['val_total_loss'].isin([float('inf'), float('-inf')])]
    ax3.plot(df_val_clean['epoch'], df_val_clean['val_total_loss'], label='Val Total Loss', linewidth=2)
    ax3.set_xlabel('Epoch')
    ax3.set_ylabel('Total Loss')
    ax3.set_title('Total Loss (Train vs Val)', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. Precision & Recall (左中)
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(df['epoch'], df['metrics/precision(B)'], label='Precision', linewidth=2, marker='o', markersize=3, markevery=10)
    ax4.plot(df['epoch'], df['metrics/recall(B)'], label='Recall', linewidth=2, marker='s', markersize=3, markevery=10)
    ax4.set_xlabel('Epoch')
    ax4.set_ylabel('Value')
    ax4.set_title('Precision & Recall', fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim([0, 1])

    # 5. mAP Metrics (中中)
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(df['epoch'], df['metrics/mAP50(B)'], label='mAP@0.5', linewidth=2, marker='o', markersize=3, markevery=10)
    ax5.plot(df['epoch'], df['metrics/mAP50-95(B)'], label='mAP@0.5:0.95', linewidth=2, marker='s', markersize=3, markevery=10)
    ax5.set_xlabel('Epoch')
    ax5.set_ylabel('mAP')
    ax5.set_title('mAP Metrics', fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_ylim([0, 1])

    # 6. 学习率 (右中)
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(df['epoch'], df['lr/pg0'], label='lr/pg0', linewidth=2)
    ax6.plot(df['epoch'], df['lr/pg1'], label='lr/pg1', linewidth=2)
    ax6.plot(df['epoch'], df['lr/pg2'], label='lr/pg2', linewidth=2)
    ax6.set_xlabel('Epoch')
    ax6.set_ylabel('Learning Rate')
    ax6.set_title('Learning Rate Schedule', fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    # 7. Box Loss 详细对比 (左下)
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(df['epoch'], df['train/box_loss'], label='Train', linewidth=2, alpha=0.8)
    df_box_clean = df[df['val/box_loss'].notna() & ~df['val/box_loss'].isin([float('inf'), float('-inf')])]
    ax7.plot(df_box_clean['epoch'], df_box_clean['val/box_loss'], label='Val', linewidth=2, alpha=0.8)
    ax7.set_xlabel('Epoch')
    ax7.set_ylabel('Box Loss')
    ax7.set_title('Box Loss (Train vs Val)', fontweight='bold')
    ax7.legend()
    ax7.grid(True, alpha=0.3)

    # 8. Cls Loss 详细对比 (中下)
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(df['epoch'], df['train/cls_loss'], label='Train', linewidth=2, alpha=0.8)
    df_cls_clean = df[df['val/cls_loss'].notna() & ~df['val/cls_loss'].isin([float('inf'), float('-inf')])]
    ax8.plot(df_cls_clean['epoch'], df_cls_clean['val/cls_loss'], label='Val', linewidth=2, alpha=0.8)
    ax8.set_xlabel('Epoch')
    ax8.set_ylabel('Classification Loss')
    ax8.set_title('Classification Loss (Train vs Val)', fontweight='bold')
    ax8.legend()
    ax8.grid(True, alpha=0.3)

    # 9. 训练统计摘要 (右下)
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')

    # 计算统计信息
    final_epoch = df['epoch'].iloc[-1]
    final_mAP50 = df['metrics/mAP50(B)'].iloc[-1]
    final_mAP50_95 = df['metrics/mAP50-95(B)'].iloc[-1]
    final_precision = df['metrics/precision(B)'].iloc[-1]
    final_recall = df['metrics/recall(B)'].iloc[-1]
    final_train_loss = df['train_total_loss'].iloc[-1]

    best_mAP50_epoch = df.loc[df['metrics/mAP50(B)'].idxmax(), 'epoch']
    best_mAP50 = df['metrics/mAP50(B)'].max()

    stats_text = f"""
    Training Statistics:
    {'='*30}

    Total Epochs: {int(final_epoch)}

    Final Metrics (Epoch {int(final_epoch)}):
    - Precision: {final_precision:.4f}
    - Recall: {final_recall:.4f}
    - mAP@0.5: {final_mAP50:.4f}
    - mAP@0.5:0.95: {final_mAP50_95:.4f}

    Best mAP@0.5: {best_mAP50:.4f}
    (at epoch {int(best_mAP50_epoch)})

    Final Train Loss: {final_train_loss:.4f}
    """

    ax9.text(0.1, 0.9, stats_text, transform=ax9.transAxes,
             fontsize=11, verticalalignment='top', family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Training overview for {model_name} saved to: {output_path}")
    plt.close()

if __name__ == '__main__':
    # YOLOv8s
    plot_model_overview(
        '/nas03/yixuh/garbage-classification/models/garbage_yolov8s/results.csv',
        'YOLOv8s',
        '/nas03/yixuh/garbage-classification/scripts/visulization/yolov8s_training_overview.png'
    )

    # YOLOv8m
    plot_model_overview(
        '/nas03/yixuh/garbage-classification/models/garbage_yolov8m/results.csv',
        'YOLOv8m',
        '/nas03/yixuh/garbage-classification/scripts/visulization/yolov8m_training_overview.png'
    )
