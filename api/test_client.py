"""
Test client for Garbage Classification API
Example usage of the API endpoints
"""

import requests
import json
from pathlib import Path
import argparse


def test_api_health(base_url="http://localhost:8000"):
    """Test API health check endpoint"""
    print("\n" + "="*60)
    print("Testing API Health Check")
    print("="*60)

    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()

        data = response.json()
        print(json.dumps(data, indent=2))

        if data.get('status') == 'healthy' and data.get('model_loaded'):
            print("\n✓ API is healthy and ready!")
            return True
        else:
            print("\n✗ API is not ready")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_detect_trash(image_path, base_url="http://localhost:8000"):
    """Test trash detection endpoint"""
    print("\n" + "="*60)
    print(f"Testing Trash Detection")
    print(f"Image: {image_path}")
    print("="*60)

    image_path = Path(image_path)

    if not image_path.exists():
        print(f"\n✗ Error: Image not found: {image_path}")
        return None

    try:
        # Prepare file for upload
        with open(image_path, 'rb') as f:
            files = {'image': (image_path.name, f, 'image/jpeg')}

            # Send POST request
            print("\nSending request...")
            response = requests.post(
                f"{base_url}/v1/detect_trash",
                files=files
            )
            response.raise_for_status()

        # Parse response
        data = response.json()

        print(f"\nStatus: {data['status']}")
        print(f"Detection Count: {data['detection_count']}")
        print(f"Inference Time: {data['inference_time_ms']:.2f} ms")

        if data['detection_count'] > 0:
            print(f"\nDetections:")
            print("-" * 60)

            for i, detection in enumerate(data['detections'], 1):
                print(f"\nObject {i}:")
                print(f"  Specific Name: {detection['specific_name']}")
                print(f"  General Category: {detection['general_category']}")
                print(f"  Confidence: {detection['confidence']:.2%}")
                print(f"  BBox (xyxy): {detection['bbox_xyxy']}")

        else:
            print("\nNo objects detected in the image.")

        print("\n✓ Detection completed successfully!")
        return data

    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def test_get_categories(base_url="http://localhost:8000"):
    """Test get categories endpoint"""
    print("\n" + "="*60)
    print("Testing Get Categories")
    print("="*60)

    try:
        response = requests.get(f"{base_url}/v1/categories")
        response.raise_for_status()

        data = response.json()

        print(f"\nTotal Classes: {data['total_classes']}")
        print(f"\nGeneral Categories:")
        for category, count in data['general_categories'].items():
            print(f"  {category}: {count} classes")

        print("\n✓ Categories retrieved successfully!")
        return data

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def main():
    """Main test function"""
    parser = argparse.ArgumentParser(
        description="Test client for Garbage Classification API"
    )
    parser.add_argument(
        '--image',
        type=str,
        help='Path to test image'
    )
    parser.add_argument(
        '--url',
        type=str,
        default='http://localhost:8000',
        help='API base URL (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all tests'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("Garbage Classification API - Test Client")
    print("="*60)

    # Test health check
    healthy = test_api_health(args.url)

    if not healthy:
        print("\n⚠ Warning: API is not healthy. Some tests may fail.")

    # Test get categories
    if args.all or not args.image:
        test_get_categories(args.url)

    # Test detection if image provided
    if args.image:
        test_detect_trash(args.image, args.url)
    elif args.all:
        print("\n⚠ No test image provided. Skipping detection test.")
        print("  Use --image <path> to test detection.")

    print("\n" + "="*60)
    print("Tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
