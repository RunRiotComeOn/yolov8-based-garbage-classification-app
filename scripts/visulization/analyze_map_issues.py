#!/usr/bin/env python3
"""
深入分析 mAP 不理想的可能原因
从训练结果CSV和配置文件中提取关键信息
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use('Agg')

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


def analyze_training_issues(csv_path, model_name):
    """分析训练过程中的问题"""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    issues = []
    recommendations = []

    print(f"\n{'='*80}")
    print(f"分析 {model_name} 的训练问题")
    print(f"{'='*80}\n")

    # 1. 检查是否过拟合
    final_train_loss = df['train/box_loss'].iloc[-1] + df['train/cls_loss'].iloc[-1] + df['train/dfl_loss'].iloc[-1]
    df_val_clean = df[df['val/box_loss'].notna() & ~df['val/box_loss'].isin([float('inf'), float('-inf')])]
    final_val_loss = df_val_clean['val/box_loss'].iloc[-1] + df_val_clean['val/cls_loss'].iloc[-1] + df_val_clean['val/dfl_loss'].iloc[-1]

    train_val_gap = final_val_loss - final_train_loss
    print(f"1. 过拟合检查:")
    print(f"   训练损失: {final_train_loss:.4f}")
    print(f"   验证损失: {final_val_loss:.4f}")
    print(f"   差距: {train_val_gap:.4f}")

    if train_val_gap > 0.5:
        issues.append("过拟合严重: 验证损失远高于训练损失")
        recommendations.append("- 增强数据增强 (更强的augmentation)")
        recommendations.append("- 增加 dropout")
        recommendations.append("- 增加 weight_decay")
        recommendations.append("- 使用更多的训练数据")
        print(f"   ⚠️  警告: 存在过拟合! (差距 > 0.5)")
    else:
        print(f"   ✓ 过拟合情况可控")

    # 2. 检查损失下降趋势
    print(f"\n2. 损失收敛分析:")
    last_50_epochs = df.tail(50)
    train_loss_std = last_50_epochs['train/box_loss'].std()
    val_loss_std = df_val_clean.tail(50)['val/box_loss'].std()

    print(f"   最后50个epoch训练损失标准差: {train_loss_std:.4f}")
    print(f"   最后50个epoch验证损失标准差: {val_loss_std:.4f}")

    if train_loss_std < 0.01:
        issues.append("训练损失已收敛但mAP较低")
        recommendations.append("- 考虑从更好的预训练模型开始")
        recommendations.append("- 检查数据标注质量")
        recommendations.append("- 可能需要更复杂的模型 (yolov8l/x)")
        print(f"   ⚠️  训练损失已收敛，但性能不理想")
    else:
        print(f"   ✓ 训练损失仍在下降，可以训练更多epoch")
        recommendations.append("- 增加训练epoch数 (200-300)")

    # 3. 检查各类损失的比例
    print(f"\n3. 损失成分分析:")
    final_box_loss = df['train/box_loss'].iloc[-1]
    final_cls_loss = df['train/cls_loss'].iloc[-1]
    final_dfl_loss = df['train/dfl_loss'].iloc[-1]

    print(f"   Box Loss: {final_box_loss:.4f} ({final_box_loss/final_train_loss*100:.1f}%)")
    print(f"   Cls Loss: {final_cls_loss:.4f} ({final_cls_loss/final_train_loss*100:.1f}%)")
    print(f"   DFL Loss: {final_dfl_loss:.4f} ({final_dfl_loss/final_train_loss*100:.1f}%)")

    if final_cls_loss / final_train_loss > 0.5:
        issues.append("分类损失占比过高")
        recommendations.append("- 类别混淆严重，检查相似类别的标注")
        recommendations.append("- 可能需要增加 cls loss weight")
        recommendations.append("- 考虑使用 focal loss")
        print(f"   ⚠️  分类损失占比过高 (>{50}%)")

    # 4. 检查 precision 和 recall 的平衡
    print(f"\n4. Precision-Recall 平衡:")
    final_precision = df['metrics/precision(B)'].iloc[-1]
    final_recall = df['metrics/recall(B)'].iloc[-1]

    print(f"   Precision: {final_precision:.4f}")
    print(f"   Recall: {final_recall:.4f}")
    print(f"   F1-Score: {2 * (final_precision * final_recall) / (final_precision + final_recall):.4f}")

    if final_precision > final_recall + 0.1:
        issues.append("Recall 明显低于 Precision")
        recommendations.append("- 模型过于保守，漏检较多")
        recommendations.append("- 降低 conf_threshold")
        recommendations.append("- 调整 anchor boxes")
        print(f"   ⚠️  Recall 低于 Precision，存在漏检问题")
    elif final_recall > final_precision + 0.1:
        issues.append("Precision 明显低于 Recall")
        recommendations.append("- 模型过于激进，误检较多")
        recommendations.append("- 提高 conf_threshold")
        recommendations.append("- 增加负样本")
        print(f"   ⚠️  Precision 低于 Recall，存在误检问题")
    else:
        print(f"   ✓ Precision 和 Recall 相对平衡")

    # 5. mAP 分析
    print(f"\n5. mAP 性能分析:")
    final_map50 = df['metrics/mAP50(B)'].iloc[-1]
    final_map50_95 = df['metrics/mAP50-95(B)'].iloc[-1]

    print(f"   mAP@0.5: {final_map50:.4f}")
    print(f"   mAP@0.5:0.95: {final_map50_95:.4f}")
    print(f"   mAP降幅: {(final_map50 - final_map50_95)/final_map50*100:.1f}%")

    if final_map50 - final_map50_95 > 0.15:
        issues.append("mAP@0.5 到 mAP@0.5:0.95 下降明显")
        recommendations.append("- 定位精度不足，边界框不够准确")
        recommendations.append("- 增加 box loss weight")
        recommendations.append("- 使用更高分辨率训练 (imgsz=1280)")
        recommendations.append("- 检查标注框是否准确")
        print(f"   ⚠️  定位精度问题: mAP在高IoU阈值下下降显著")

    if final_map50 < 0.6:
        issues.append("总体 mAP 偏低")
        recommendations.append("- 可能是数据质量问题")
        recommendations.append("- 检查数据集大小是否足够")
        recommendations.append("- 验证数据增强是否过度")
        recommendations.append("- 考虑使用更大的模型")
        print(f"   ⚠️  整体性能偏低 (mAP@0.5 < 0.6)")

    # 6. 学习率检查
    print(f"\n6. 学习率调度:")
    initial_lr = df['lr/pg0'].iloc[0]
    final_lr = df['lr/pg0'].iloc[-1]
    print(f"   初始学习率: {initial_lr:.6f}")
    print(f"   最终学习率: {final_lr:.6f}")
    print(f"   衰减比例: {final_lr/initial_lr:.4f}")

    # 7. 早期训练阶段分析
    print(f"\n7. 早期训练分析 (前30个epoch):")
    early_df = df.head(30)
    early_map_improvement = early_df['metrics/mAP50(B)'].iloc[-1] - early_df['metrics/mAP50(B)'].iloc[0]
    print(f"   早期 mAP@0.5 提升: {early_map_improvement:.4f}")

    if early_map_improvement < 0.1:
        issues.append("早期训练阶段提升缓慢")
        recommendations.append("- 初始学习率可能太小，尝试 lr0=0.02")
        recommendations.append("- warmup epochs 可能太长")
        print(f"   ⚠️  早期提升缓慢，可能学习率设置不当")

    return issues, recommendations


def create_diagnostic_plots(csv_path, model_name, output_path):
    """创建诊断图表"""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(f'{model_name} - Diagnostic Analysis', fontsize=16, fontweight='bold')

    # 1. Train vs Val Loss
    ax = axes[0, 0]
    df['train_total'] = df['train/box_loss'] + df['train/cls_loss'] + df['train/dfl_loss']
    df_val_clean = df[df['val/box_loss'].notna() & ~df['val/box_loss'].isin([float('inf'), float('-inf')])]
    df_val_clean['val_total'] = df_val_clean['val/box_loss'] + df_val_clean['val/cls_loss'] + df_val_clean['val/dfl_loss']

    ax.plot(df['epoch'], df['train_total'], label='Train', linewidth=2)
    ax.plot(df_val_clean['epoch'], df_val_clean['val_total'], label='Val', linewidth=2)
    ax.fill_between(df_val_clean['epoch'],
                     df_val_clean['val_total'].rolling(10).mean() - df_val_clean['val_total'].rolling(10).std(),
                     df_val_clean['val_total'].rolling(10).mean() + df_val_clean['val_total'].rolling(10).std(),
                     alpha=0.2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Total Loss')
    ax.set_title('Overfitting Check: Train vs Val Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. Loss Components Ratio
    ax = axes[0, 1]
    epochs = df['epoch']
    box_ratio = df['train/box_loss'] / df['train_total']
    cls_ratio = df['train/cls_loss'] / df['train_total']
    dfl_ratio = df['train/dfl_loss'] / df['train_total']

    ax.plot(epochs, box_ratio, label='Box Loss %', linewidth=2)
    ax.plot(epochs, cls_ratio, label='Cls Loss %', linewidth=2)
    ax.plot(epochs, dfl_ratio, label='DFL Loss %', linewidth=2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss Ratio')
    ax.set_title('Loss Component Distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. Precision-Recall Curve
    ax = axes[0, 2]
    ax.plot(df['epoch'], df['metrics/precision(B)'], label='Precision', linewidth=2, marker='o', markersize=2, markevery=10)
    ax.plot(df['epoch'], df['metrics/recall(B)'], label='Recall', linewidth=2, marker='s', markersize=2, markevery=10)

    # 添加 F1-Score
    f1_score = 2 * (df['metrics/precision(B)'] * df['metrics/recall(B)']) / (df['metrics/precision(B)'] + df['metrics/recall(B)'])
    ax.plot(df['epoch'], f1_score, label='F1-Score', linewidth=2, linestyle='--')

    ax.set_xlabel('Epoch')
    ax.set_ylabel('Metric Value')
    ax.set_title('Precision-Recall Balance')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1])

    # 4. mAP Gap Analysis
    ax = axes[1, 0]
    map_gap = df['metrics/mAP50(B)'] - df['metrics/mAP50-95(B)']
    ax.plot(df['epoch'], map_gap, linewidth=2, color='red')
    ax.fill_between(df['epoch'], 0, map_gap, alpha=0.3, color='red')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('mAP Gap')
    ax.set_title('Localization Accuracy (mAP@0.5 - mAP@0.5:0.95)')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0.15, color='orange', linestyle='--', label='Threshold (0.15)')
    ax.legend()

    # 5. Learning Rate
    ax = axes[1, 1]
    ax.plot(df['epoch'], df['lr/pg0'], linewidth=2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Learning Rate')
    ax.set_title('Learning Rate Schedule')
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # 6. mAP Improvement Rate
    ax = axes[1, 2]
    map_diff = df['metrics/mAP50(B)'].diff().rolling(10).mean()
    ax.plot(df['epoch'].iloc[1:], map_diff.iloc[1:], linewidth=2)
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('mAP Change (smoothed)')
    ax.set_title('mAP Improvement Rate (10-epoch avg)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n诊断图表已保存到: {output_path}")
    plt.close()


def main():
    models = [
        {
            'csv': '/nas03/yixuh/garbage-classification/models/garbage_yolov8s/results.csv',
            'name': 'YOLOv8s',
            'plot': '/nas03/yixuh/garbage-classification/scripts/visulization/yolov8s_diagnostics.png'
        },
        {
            'csv': '/nas03/yixuh/garbage-classification/models/garbage_yolov8m/results.csv',
            'name': 'YOLOv8m',
            'plot': '/nas03/yixuh/garbage-classification/scripts/visulization/yolov8m_diagnostics.png'
        }
    ]

    all_issues = {}
    all_recommendations = {}

    for model in models:
        issues, recommendations = analyze_training_issues(model['csv'], model['name'])
        all_issues[model['name']] = issues
        all_recommendations[model['name']] = recommendations

        create_diagnostic_plots(model['csv'], model['name'], model['plot'])

    # 生成综合报告
    print(f"\n{'='*80}")
    print("综合诊断报告")
    print(f"{'='*80}\n")

    for model_name in all_issues.keys():
        print(f"\n{model_name} 发现的问题:")
        print("-" * 80)
        if all_issues[model_name]:
            for i, issue in enumerate(all_issues[model_name], 1):
                print(f"{i}. {issue}")
        else:
            print("未发现明显问题")

        print(f"\n{model_name} 改进建议:")
        print("-" * 80)
        if all_recommendations[model_name]:
            for rec in all_recommendations[model_name]:
                print(f"{rec}")
        else:
            print("暂无特殊建议")

    # 通用建议
    print(f"\n{'='*80}")
    print("通用改进建议 (基于垃圾分类任务特点)")
    print(f"{'='*80}")

    general_recommendations = [
        "\n📊 数据方面:",
        "- 检查数据集大小: 垃圾分类通常需要每类至少500-1000张图片",
        "- 验证标注质量: 检查边界框是否准确，类别是否标注正确",
        "- 类别平衡: 检查各类别样本数量是否均衡",
        "- 数据多样性: 确保包含不同光照、角度、背景的图片",

        "\n🔧 模型配置:",
        "- 考虑使用更大的模型 (YOLOv8l 或 YOLOv8x)",
        "- 增加训练分辨率 (imgsz=1280)",
        "- 调整 anchor boxes 以适应垃圾物体的尺寸分布",

        "\n🎯 训练策略:",
        "- 增加训练轮数到 200-300 epochs",
        "- 使用 cosine learning rate schedule (cos_lr=True)",
        "- 尝试不同的 optimizer (SGD vs AdamW)",
        "- 调整 batch size (更大的 batch size 可能更稳定)",

        "\n🌈 数据增强:",
        "- 垃圾分类场景可能需要更强的颜色增强",
        "- 适当增加 mosaic 和 mixup 概率",
        "- 考虑添加模糊、噪声等增强",

        "\n📈 其他:",
        "- 使用预训练权重 (COCO dataset)",
        "- 实施 class-weighted loss 处理类别不平衡",
        "- 尝试 test-time augmentation (TTA)",
        "- 进行错误分析，查看哪些类别容易混淆"
    ]

    for rec in general_recommendations:
        print(rec)

    print(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()
