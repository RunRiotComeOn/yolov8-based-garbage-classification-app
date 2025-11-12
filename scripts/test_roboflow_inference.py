"""
Test Roboflow Inference API
Use Roboflow's serverless inference for garbage classification
"""

import os
import sys
from pathlib import Path
import json


def test_inference(image_path, api_key="sIWvnNEtbUWeBxn0ZhWq"):
    """
    Test Roboflow inference API

    Args:
        image_path: Path to test image
        api_key: Roboflow API key
    """
    try:
        from inference_sdk import InferenceHTTPClient
    except ImportError:
        print("Installing inference-sdk package...")
        os.system(f"{sys.executable} -m pip install inference-sdk")
        from inference_sdk import InferenceHTTPClient

    print(f"\n{'='*60}")
    print("Testing Roboflow Inference API")
    print(f"{'='*60}\n")

    # Initialize client
    CLIENT = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key=api_key
    )

    print(f"Image: {image_path}")
    print(f"Model: garbage-classification-3/2")
    print(f"API URL: https://serverless.roboflow.com")
    print(f"API Key: {api_key[:8]}...\n")

    # Run inference
    print("Running inference...")
    result = CLIENT.infer(image_path, model_id="garbage-classification-3/2")

    print(f"\n{'='*60}")
    print("Inference Results")
    print(f"{'='*60}\n")

    # Print results
    print(json.dumps(result, indent=2))

    # Parse and display detections
    if 'predictions' in result:
        predictions = result['predictions']
        print(f"\n{'='*60}")
        print(f"Detected {len(predictions)} objects:")
        print(f"{'='*60}\n")

        for i, pred in enumerate(predictions, 1):
            print(f"{i}. {pred['class']}")
            print(f"   Confidence: {pred['confidence']:.3f}")
            print(f"   BBox: ({pred['x']:.1f}, {pred['y']:.1f}, {pred['width']:.1f}, {pred['height']:.1f})")
            print()

    return result


def compare_with_local_model(image_path):
    """
    Compare Roboflow API results with local YOLOv8 model

    Args:
        image_path: Path to test image
    """
    print(f"\n{'='*60}")
    print("Comparing Roboflow API vs Local Model")
    print(f"{'='*60}\n")

    # Test Roboflow API
    print("1. Testing Roboflow Serverless API...")
    roboflow_result = test_inference(image_path)

    # Test local model if available
    try:
        from ultralytics import YOLO
        import cv2
        import time

        project_root = Path(__file__).parent.parent
        model_path = project_root / 'models' / 'garbage_yolov8s' / 'weights' / 'best.pt'

        if model_path.exists():
            print("\n2. Testing Local YOLOv8 Model...")

            model = YOLO(str(model_path))
            img = cv2.imread(str(image_path))

            start_time = time.time()
            results = model(img)
            inference_time = (time.time() - start_time) * 1000

            print(f"Local model inference time: {inference_time:.2f}ms")

            if len(results) > 0:
                boxes = results[0].boxes
                print(f"Detected {len(boxes)} objects\n")

                for i, box in enumerate(boxes, 1):
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    print(f"{i}. Class {cls}")
                    print(f"   Confidence: {conf:.3f}")
                    print()
        else:
            print("\n2. Local model not found. Train the model first!")
            print(f"   Expected: {model_path}")

    except ImportError:
        print("\n2. Ultralytics not installed. Install with: pip install ultralytics")


def batch_test(image_dir, api_key="sIWvnNEtbUWeBxn0ZhWq"):
    """
    Test inference on a batch of images

    Args:
        image_dir: Directory containing test images
        api_key: Roboflow API key
    """
    image_dir = Path(image_dir)

    if not image_dir.exists():
        print(f"Error: Directory not found: {image_dir}")
        return

    # Find all images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    images = []
    for ext in image_extensions:
        images.extend(image_dir.glob(f"*{ext}"))

    if not images:
        print(f"No images found in {image_dir}")
        return

    print(f"\n{'='*60}")
    print(f"Batch Testing on {len(images)} images")
    print(f"{'='*60}\n")

    results = []
    for i, img_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Testing: {img_path.name}")
        try:
            result = test_inference(str(img_path), api_key)
            results.append({
                'image': img_path.name,
                'result': result,
                'success': True
            })
        except Exception as e:
            print(f"Error: {e}")
            results.append({
                'image': img_path.name,
                'error': str(e),
                'success': False
            })

    # Summary
    print(f"\n{'='*60}")
    print("Batch Test Summary")
    print(f"{'='*60}\n")

    successful = sum(1 for r in results if r['success'])
    print(f"Total images: {len(images)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(images) - successful}")

    return results


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Test Roboflow Inference API')
    parser.add_argument('--image', type=str, help='Path to test image')
    parser.add_argument('--api-key', type=str, default='sIWvnNEtbUWeBxn0ZhWq',
                        help='Roboflow API key')
    parser.add_argument('--compare', action='store_true',
                        help='Compare with local model')
    parser.add_argument('--batch', type=str,
                        help='Directory for batch testing')

    args = parser.parse_args()

    if args.batch:
        # Batch test
        batch_test(args.batch, args.api_key)
    elif args.image:
        if args.compare:
            # Compare with local model
            compare_with_local_model(args.image)
        else:
            # Single image test
            test_inference(args.image, args.api_key)
    else:
        print("Please provide --image or --batch")
        parser.print_help()


if __name__ == "__main__":
    main()
