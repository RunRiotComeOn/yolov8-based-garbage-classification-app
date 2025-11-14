#!/usr/bin/env python3
"""
一键运行所有可视化脚本
"""
import subprocess
import sys
import os

scripts = [
    'plot_loss_comparison.py',
    'plot_metrics_comparison.py',
    'plot_training_overview.py'
]

script_dir = '/nas03/yixuh/garbage-classification/scripts/visulization'

print("="*60)
print("Running all visualization scripts...")
print("="*60)

for script in scripts:
    script_path = os.path.join(script_dir, script)
    print(f"\n>>> Running {script}...")
    try:
        result = subprocess.run(['python3', script_path],
                              capture_output=True,
                              text=True,
                              check=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}:")
        print(e.stderr)
        sys.exit(1)

print("\n" + "="*60)
print("All visualizations completed successfully!")
print("="*60)
print("\nGenerated plots:")
print("  1. loss_comparison.png - Loss comparison between models")
print("  2. metrics_comparison.png - Metrics comparison between models")
print("  3. yolov8s_training_overview.png - YOLOv8s detailed overview")
print("  4. yolov8m_training_overview.png - YOLOv8m detailed overview")
print(f"\nOutput directory: {script_dir}")
