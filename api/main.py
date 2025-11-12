"""
FastAPI Service for Garbage Classification
Provides API endpoint for real-time trash detection and classification
"""

import os
import json
import io
from pathlib import Path
from typing import List, Dict, Optional
import logging

import numpy as np
import cv2
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from ultralytics import YOLO
import torch


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic models for API response
class Detection(BaseModel):
    """Single object detection result"""
    bbox_xyxy: List[float] = Field(
        ...,
        description="Bounding box coordinates [x1, y1, x2, y2]"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Detection confidence score"
    )
    specific_name: str = Field(
        ...,
        description="Specific trash category (L1 label)"
    )
    general_category: str = Field(
        ...,
        description="General disposal category (L2 label): Recycle/Trash/Hazardous/Organic"
    )


class DetectionResponse(BaseModel):
    """API response model"""
    status: str = Field(
        default="success",
        description="Request status"
    )
    detection_count: int = Field(
        ...,
        ge=0,
        description="Number of objects detected"
    )
    detections: List[Detection] = Field(
        default_factory=list,
        description="List of detected objects"
    )
    inference_time_ms: float = Field(
        ...,
        description="Model inference time in milliseconds"
    )


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str
    detail: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="Garbage Classification API",
    description="Real-time trash detection and classification using YOLOv8",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Global variables for model and category mapping
model = None
category_mapping = None


def load_model(model_path: str = None):
    """Load YOLOv8 model"""
    global model

    if model_path is None:
        # Default model path
        project_root = Path(__file__).parent.parent
        model_path = project_root / "models" / "garbage_yolov8s" / "weights" / "best.pt"

    model_path = Path(model_path)

    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        raise FileNotFoundError(f"Model file not found: {model_path}")

    logger.info(f"Loading model from: {model_path}")

    try:
        model = YOLO(str(model_path))

        # Check if GPU is available
        if torch.cuda.is_available():
            device = torch.cuda.get_device_name(0)
            logger.info(f"Using GPU: {device}")
        else:
            logger.warning("GPU not available, using CPU (slower inference)")

        logger.info("Model loaded successfully!")
        return model

    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


def load_category_mapping(mapping_path: str = None):
    """Load category mapping from JSON file"""
    global category_mapping

    if mapping_path is None:
        # Default mapping path
        project_root = Path(__file__).parent.parent
        mapping_path = project_root / "configs" / "category_mapping.json"

    mapping_path = Path(mapping_path)

    if not mapping_path.exists():
        logger.error(f"Category mapping not found: {mapping_path}")
        raise FileNotFoundError(f"Category mapping file not found: {mapping_path}")

    logger.info(f"Loading category mapping from: {mapping_path}")

    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            category_mapping = data['mapping']

        logger.info(f"Category mapping loaded: {len(category_mapping)} categories")
        return category_mapping

    except Exception as e:
        logger.error(f"Failed to load category mapping: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize model and mappings on startup"""
    logger.info("="*60)
    logger.info("Starting Garbage Classification API")
    logger.info("="*60)

    try:
        # Load model
        load_model()

        # Load category mapping
        load_category_mapping()

        logger.info("API initialized successfully!")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        logger.error("Please ensure the model is trained and category mapping exists")
        raise


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "service": "Garbage Classification API",
        "status": "running",
        "version": "1.0.0",
        "model": "YOLOv8m",
        "dataset": "TACO",
        "endpoints": {
            "detection": "/v1/detect_trash",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    gpu_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_available else "N/A"

    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "category_mapping_loaded": category_mapping is not None,
        "gpu_available": gpu_available,
        "gpu_name": gpu_name
    }


@app.post(
    "/v1/detect_trash",
    response_model=DetectionResponse,
    responses={
        200: {"description": "Successful detection"},
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"}
    },
    tags=["Detection"]
)
async def detect_trash(
    image: UploadFile = File(..., description="Image file to analyze")
):
    """
    Detect and classify trash in uploaded image

    Returns:
        - detection_count: Number of trash items detected
        - detections: List of detections with bounding boxes, confidence scores,
                     specific names (L1), and general categories (L2)
    """

    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {image.content_type}. Please upload an image file."
        )

    try:
        # Read image file
        contents = await image.read()
        image_bytes = io.BytesIO(contents)

        # Convert to PIL Image
        pil_image = Image.open(image_bytes)

        # Convert to numpy array (RGB)
        img_array = np.array(pil_image)

        # If image has alpha channel, remove it
        if img_array.shape[-1] == 4:
            img_array = img_array[..., :3]

        logger.info(f"Processing image: {image.filename} | Shape: {img_array.shape}")

        # Run inference
        import time
        start_time = time.time()

        results = model(img_array, conf=0.25, iou=0.45)  # conf threshold, iou threshold

        inference_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Process results
        detections = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                # Get bounding box coordinates (xyxy format)
                bbox = box.xyxy[0].cpu().numpy().tolist()

                # Get confidence score
                confidence = float(box.conf[0].cpu().numpy())

                # Get class ID and name
                class_id = int(box.cls[0].cpu().numpy())
                specific_name = model.names[class_id]

                # Map to general category (L2 label)
                general_category = category_mapping.get(specific_name, "Unknown")

                # Create detection object
                detection = Detection(
                    bbox_xyxy=bbox,
                    confidence=confidence,
                    specific_name=specific_name,
                    general_category=general_category
                )

                detections.append(detection)

        logger.info(
            f"Detection complete: {len(detections)} objects found | "
            f"Inference time: {inference_time:.2f}ms"
        )

        # Create response
        response = DetectionResponse(
            status="success",
            detection_count=len(detections),
            detections=detections,
            inference_time_ms=round(inference_time, 2)
        )

        return response

    except Exception as e:
        logger.error(f"Error during detection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.get("/v1/categories", tags=["Info"])
async def get_categories():
    """Get all supported categories and their mappings"""
    if category_mapping is None:
        raise HTTPException(status_code=500, detail="Category mapping not loaded")

    # Count categories by type
    category_counts = {}
    for specific, general in category_mapping.items():
        category_counts[general] = category_counts.get(general, 0) + 1

    return {
        "total_classes": len(category_mapping),
        "specific_categories": list(category_mapping.keys()),
        "general_categories": {
            "Recycle": category_counts.get("Recycle", 0),
            "Trash": category_counts.get("Trash", 0),
            "Hazardous": category_counts.get("Hazardous", 0),
            "Organic": category_counts.get("Organic", 0)
        },
        "mapping": category_mapping
    }


if __name__ == "__main__":
    import uvicorn

    # Run the API server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
