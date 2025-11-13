class DetectionResponse {
  final String status;
  final int detectionCount;
  final List<Detection> detections;
  final double inferenceTimeMs;

  DetectionResponse({
    required this.status,
    required this.detectionCount,
    required this.detections,
    required this.inferenceTimeMs,
  });

  factory DetectionResponse.fromJson(Map<String, dynamic> json) {
    var list = json['detections'] as List;
    List<Detection> detectionsList =
        list.map((i) => Detection.fromJson(i)).toList();

    return DetectionResponse(
      status: json['status'],
      detectionCount: json['detection_count'],
      detections: detectionsList,
      inferenceTimeMs: (json['inference_time_ms'] as num).toDouble(),
    );
  }
}

class Detection {
  final List<double> bboxXyxy;
  final double confidence;
  final String specificName;
  final String generalCategory;

  Detection({
    required this.bboxXyxy,
    required this.confidence,
    required this.specificName,
    required this.generalCategory,
  });

  factory Detection.fromJson(Map<String, dynamic> json) {
    return Detection(
      bboxXyxy:
          List<double>.from(json['bbox_xyxy'].map((x) => (x as num).toDouble())),
      confidence: (json['confidence'] as num).toDouble(),
      specificName: json['specific_name'],
      generalCategory: json['general_category'],
    );
  }
}

