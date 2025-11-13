import 'package:flutter/material.dart';
import '../models/detection.dart';

/// Custom painter for drawing detection bounding boxes
class DetectionPainter extends CustomPainter {
  final List<Detection> detections;
  final Size imageSize;

  DetectionPainter({
    required this.detections,
    required this.imageSize,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final scaleX = size.width / imageSize.width;
    final scaleY = size.height / imageSize.height;

    for (final detection in detections) {
      final bbox = detection.bboxXyxy;
      if (bbox.length < 4) continue;

      final x1 = bbox[0] * scaleX;
      final y1 = bbox[1] * scaleY;
      final x2 = bbox[2] * scaleX;
      final y2 = bbox[3] * scaleY;

      // Draw bounding box
      final rect = Rect.fromLTRB(x1, y1, x2, y2);
      final paint = Paint()
        ..color = _getColorForClass(detection.specificName)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.0;

      canvas.drawRect(rect, paint);

      // Draw label background
      final label = '${detection.specificName} ${(detection.confidence * 100).toStringAsFixed(1)}%';
      final textPainter = TextPainter(
        text: TextSpan(
          text: label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();

      final labelRect = Rect.fromLTWH(
        x1,
        y1 - textPainter.height - 4,
        textPainter.width + 8,
        textPainter.height + 4,
      );

      final labelPaint = Paint()
        ..color = _getColorForClass(detection.specificName);

      canvas.drawRect(labelRect, labelPaint);

      // Draw label text
      textPainter.paint(canvas, Offset(x1 + 4, y1 - textPainter.height - 2));
    }
  }

  Color _getColorForClass(String className) {
    switch (className.toUpperCase()) {
      case 'PLASTIC':
        return Colors.blue;
      case 'PAPER':
      case 'CARDBOARD':
        return Colors.brown;
      case 'GLASS':
        return Colors.cyan;
      case 'METAL':
        return Colors.grey;
      case 'BIODEGRADABLE':
        return Colors.green;
      default:
        return Colors.red;
    }
  }

  @override
  bool shouldRepaint(DetectionPainter oldDelegate) {
    return oldDelegate.detections != detections ||
           oldDelegate.imageSize != imageSize;
  }
}

/// Detection overlay widget
class DetectionOverlay extends StatelessWidget {
  final List<Detection> detections;
  final Size imageSize;
  final Widget child;

  const DetectionOverlay({
    super.key,
    required this.detections,
    required this.imageSize,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (detections.isNotEmpty)
          Positioned.fill(
            child: CustomPaint(
              painter: DetectionPainter(
                detections: detections,
                imageSize: imageSize,
              ),
            ),
          ),
      ],
    );
  }
}
