"""
Download Garbage Classification Dataset from Roboflow
Dataset: GARBAGE CLASSIFICATION 3
- 10,464 images
- 7 classes: BIODEGRADABLE, CARDBOARD, CLOTH, GLASS, METAL, PAPER, PLASTIC
"""

import os
import sys
from pathlib import Path
import shutil


def download_from_roboflow(api_key=None):
    """Download dataset using Roboflow API"""
    try:
        from roboflow import Roboflow
    except ImportError:
        print("Installing roboflow package...")
        os.system(f"{sys.executable} -m pip install roboflow")
        from roboflow import Roboflow

    # Get project root
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    raw_dir = data_dir / 'raw'
    processed_dir = data_dir / 'processed'

    # Create directories
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("Downloading Garbage Classification Dataset from Roboflow")
    print(f"{'='*60}\n")

    # Use provided API key or default
    if api_key is None:
        api_key = "sIWvnNEtbUWeBxn0ZhWq"  # Default API key

    print(f"Using API key: {api_key[:8]}...")

    # Initialize Roboflow
    rf = Roboflow(api_key=api_key)

    # Download dataset
    # Dataset: GARBAGE CLASSIFICATION 3
    # Link: https://universe.roboflow.com/material-identification/garbage-classification-3
    project = rf.workspace("material-identification").project("garbage-classification-3")

    # Download in YOLOv8 format
    print("Downloading dataset in YOLOv8 format...")
    dataset = project.version(2).download("yolov8", location=str(raw_dir))

    print(f"\n{'='*60}")
    print("Dataset downloaded successfully!")
    print(f"Location: {dataset.location}")
    print(f"{'='*60}\n")

    return dataset.location


def download_from_url():
    """
    Alternative: Download from direct link (without API key)
    Users can download manually from:
    https://universe.roboflow.com/material-identification/garbage-classification-3
    """
    print("\n" + "="*60)
    print("Manual Download Instructions")
    print("="*60)
    print("\nOption 1: Using Roboflow API")
    print("1. Create a free account at https://roboflow.com")
    print("2. Get your API key from https://app.roboflow.com/settings/api")
    print("3. Edit this script and replace YOUR_API_KEY with your actual key")
    print("4. Run: python scripts/download_garbage_dataset.py")
    print("\nOption 2: Manual Download")
    print("1. Visit: https://universe.roboflow.com/material-identification/garbage-classification-3")
    print("2. Click 'Download Dataset'")
    print("3. Select 'YOLOv8' format")
    print("4. Download and extract to: data/raw/")
    print("="*60 + "\n")


def organize_dataset(dataset_path):
    """Organize the downloaded dataset into processed folder"""
    project_root = Path(__file__).parent.parent
    processed_dir = project_root / 'data' / 'processed'

    dataset_path = Path(dataset_path)

    print(f"\n{'='*60}")
    print("Organizing dataset...")
    print(f"{'='*60}\n")

    # Copy dataset structure
    for split in ['train', 'valid', 'test']:
        src_images = dataset_path / split / 'images'
        src_labels = dataset_path / split / 'labels'

        if src_images.exists():
            dst_images = processed_dir / 'images' / split
            dst_labels = processed_dir / 'labels' / split

            # Create directories
            dst_images.mkdir(parents=True, exist_ok=True)
            dst_labels.mkdir(parents=True, exist_ok=True)

            # Copy files
            if not any(dst_images.iterdir()):
                shutil.copytree(src_images, dst_images, dirs_exist_ok=True)
                print(f"✓ Copied {split} images")

            if src_labels.exists() and not any(dst_labels.iterdir()):
                shutil.copytree(src_labels, dst_labels, dirs_exist_ok=True)
                print(f"✓ Copied {split} labels")

    # Copy data.yaml if it exists
    src_yaml = dataset_path / 'data.yaml'
    if src_yaml.exists():
        dst_yaml = project_root / 'configs' / 'garbage.yaml'

        # Read and modify yaml
        with open(src_yaml, 'r') as f:
            yaml_content = f.read()

        # Update paths to use absolute paths
        yaml_content = yaml_content.replace(
            'train: ../train/images',
            f'train: {processed_dir}/images/train'
        )
        yaml_content = yaml_content.replace(
            'val: ../valid/images',
            f'val: {processed_dir}/images/valid'
        )
        yaml_content = yaml_content.replace(
            'test: ../test/images',
            f'test: {processed_dir}/images/test'
        )

        with open(dst_yaml, 'w') as f:
            f.write(yaml_content)

        print(f"✓ Created config file: {dst_yaml}")

    print(f"\n{'='*60}")
    print("Dataset organized successfully!")
    print(f"{'='*60}\n")

    # Print statistics
    train_images = list((processed_dir / 'images' / 'train').glob('*'))
    valid_images = list((processed_dir / 'images' / 'valid').glob('*'))
    test_images = list((processed_dir / 'images' / 'test').glob('*'))

    print("Dataset Statistics:")
    print(f"  Train: {len(train_images)} images")
    print(f"  Valid: {len(valid_images)} images")
    print(f"  Test: {len(test_images)} images")
    print(f"  Total: {len(train_images) + len(valid_images) + len(test_images)} images\n")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Download Garbage Classification Dataset')
    parser.add_argument('--api-key', type=str, help='Roboflow API key')
    parser.add_argument('--manual', action='store_true',
                        help='Show manual download instructions')
    parser.add_argument('--organize', type=str,
                        help='Organize already downloaded dataset from path')

    args = parser.parse_args()

    if args.manual:
        download_from_url()
        return

    if args.organize:
        organize_dataset(args.organize)
        return

    if args.api_key:
        # Download using API
        print("Using Roboflow API to download dataset...")
        dataset_path = download_from_roboflow(api_key=args.api_key)
        organize_dataset(dataset_path)
    else:
        # Use default API key if no argument provided
        print("Using default Roboflow API to download dataset...")
        print("(You can provide your own key with --api-key YOUR_KEY)\n")
        try:
            dataset_path = download_from_roboflow()
            organize_dataset(dataset_path)
        except Exception as e:
            print(f"\nError downloading dataset: {e}")
            print("\nFalling back to manual instructions...\n")
            download_from_url()


if __name__ == "__main__":
    main()
