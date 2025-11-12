"""
Environment Verification Script
Checks if all dependencies and configurations are properly set up
"""

import sys
import os
from pathlib import Path
import json


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60)


def print_check(name, passed, message=""):
    """Print check result"""
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"  # Green or Red
    reset = "\033[0m"

    print(f"{color}{status}{reset} {name}")
    if message:
        print(f"  {message}")


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    required = (3, 8)
    passed = version >= required

    message = f"Python {version.major}.{version.minor}.{version.micro}"
    if not passed:
        message += f" (Required: >= {required[0]}.{required[1]})"

    print_check("Python Version", passed, message)
    return passed


def check_imports():
    """Check if required packages are installed"""
    print("\nChecking Python packages...")

    packages = {
        'torch': 'PyTorch',
        'torchvision': 'TorchVision',
        'ultralytics': 'Ultralytics YOLOv8',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'cv2': 'OpenCV (opencv-python)',
        'PIL': 'Pillow',
        'numpy': 'NumPy',
        'yaml': 'PyYAML (pyyaml)',
        'pydantic': 'Pydantic',
        'pycocotools': 'COCO Tools',
        'requests': 'Requests',
        'tqdm': 'tqdm'
    }

    all_passed = True

    for module_name, package_name in packages.items():
        try:
            __import__(module_name)
            print_check(package_name, True)
        except ImportError as e:
            print_check(package_name, False, f"Import error: {e}")
            all_passed = False

    return all_passed


def check_cuda():
    """Check CUDA availability"""
    print("\nChecking GPU/CUDA...")

    try:
        import torch

        cuda_available = torch.cuda.is_available()
        print_check("CUDA Available", cuda_available)

        if cuda_available:
            gpu_count = torch.cuda.device_count()
            print_check("GPU Count", True, f"{gpu_count} GPU(s) detected")

            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                print_check(
                    f"GPU {i}",
                    True,
                    f"{gpu_name} ({gpu_memory:.1f} GB)"
                )

            cuda_version = torch.version.cuda
            print_check("CUDA Version", True, cuda_version)
        else:
            print("  Warning: Training and inference will be slow without GPU")

        return True

    except Exception as e:
        print_check("CUDA Check", False, str(e))
        return False


def check_project_structure():
    """Check project directory structure"""
    print("\nChecking project structure...")

    project_root = Path(__file__).parent.parent

    required_dirs = [
        'api',
        'configs',
        'data',
        'models',
        'scripts'
    ]

    required_files = [
        'requirements.txt',
        'README.md',
        'configs/taco.yaml',
        'configs/category_mapping.json',
        'api/main.py',
        'scripts/prepare_taco_dataset.py',
        'scripts/train_yolov8.py'
    ]

    all_passed = True

    # Check directories
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        passed = dir_path.exists() and dir_path.is_dir()
        print_check(f"Directory: {dir_name}/", passed)
        all_passed = all_passed and passed

    # Check files
    for file_path in required_files:
        full_path = project_root / file_path
        passed = full_path.exists() and full_path.is_file()
        print_check(f"File: {file_path}", passed)
        all_passed = all_passed and passed

    return all_passed


def check_dataset():
    """Check if dataset is prepared"""
    print("\nChecking dataset...")

    project_root = Path(__file__).parent.parent
    processed_data_dir = project_root / "data" / "processed"

    # Check if processed data directory exists
    if not processed_data_dir.exists():
        print_check(
            "Dataset",
            False,
            "Dataset not prepared. Run: python scripts/prepare_taco_dataset.py"
        )
        return False

    # Check for train/val/test splits
    splits = ['train', 'val', 'test']
    all_passed = True

    for split in splits:
        images_dir = processed_data_dir / 'images' / split
        labels_dir = processed_data_dir / 'labels' / split

        if images_dir.exists() and labels_dir.exists():
            image_count = len(list(images_dir.glob('*.jpg'))) + len(list(images_dir.glob('*.png')))
            label_count = len(list(labels_dir.glob('*.txt')))

            print_check(
                f"{split.capitalize()} set",
                True,
                f"{image_count} images, {label_count} labels"
            )
        else:
            print_check(f"{split.capitalize()} set", False, "Missing")
            all_passed = False

    if not all_passed:
        print("  Run: python scripts/prepare_taco_dataset.py")

    return all_passed


def check_model():
    """Check if model is trained"""
    print("\nChecking trained model...")

    project_root = Path(__file__).parent.parent
    model_path = project_root / "models" / "taco_yolov8m" / "weights" / "best.pt"

    if model_path.exists():
        size_mb = model_path.stat().st_size / 1024**2
        print_check("Trained Model", True, f"{model_path.name} ({size_mb:.1f} MB)")
        return True
    else:
        print_check(
            "Trained Model",
            False,
            "Model not found. Run: python scripts/train_yolov8.py"
        )
        return False


def check_configs():
    """Check configuration files"""
    print("\nChecking configuration files...")

    project_root = Path(__file__).parent.parent

    # Check taco.yaml
    taco_yaml_path = project_root / "configs" / "taco.yaml"
    if taco_yaml_path.exists():
        print_check("TACO Dataset Config", True, str(taco_yaml_path.name))
    else:
        print_check("TACO Dataset Config", False)
        return False

    # Check category_mapping.json
    mapping_path = project_root / "configs" / "category_mapping.json"
    if mapping_path.exists():
        try:
            with open(mapping_path, 'r') as f:
                data = json.load(f)
                mapping_count = len(data.get('mapping', {}))
                print_check(
                    "Category Mapping",
                    True,
                    f"{mapping_count} categories mapped"
                )
        except Exception as e:
            print_check("Category Mapping", False, f"Error reading file: {e}")
            return False
    else:
        print_check("Category Mapping", False)
        return False

    return True


def main():
    """Main verification function"""
    print_header("Environment Verification")
    print("This script checks if your environment is properly configured")
    print("for the Garbage Classification project.")

    results = {}

    # Run all checks
    print_header("System Information")
    results['python'] = check_python_version()
    results['cuda'] = check_cuda()

    print_header("Python Dependencies")
    results['imports'] = check_imports()

    print_header("Project Structure")
    results['structure'] = check_project_structure()
    results['configs'] = check_configs()

    print_header("Data & Model")
    results['dataset'] = check_dataset()
    results['model'] = check_model()

    # Summary
    print_header("Summary")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\nChecks passed: {passed_count}/{total_count}")

    if all(results.values()):
        print("\n✓ All checks passed! Your environment is ready.")
        print("\nNext steps:")
        print("  1. If dataset is not prepared: python scripts/prepare_taco_dataset.py")
        print("  2. If model is not trained: python scripts/train_yolov8.py")
        print("  3. Start API server: ./start_api.sh")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Missing packages: pip install -r requirements.txt")
        print("  - Missing dataset: python scripts/prepare_taco_dataset.py")
        print("  - Missing model: python scripts/train_yolov8.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
