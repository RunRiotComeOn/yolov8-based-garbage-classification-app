import 'dart:io';
import 'package:flutter/material.dart';
import '../models/detection.dart';
import '../services/api_service.dart';
import '../services/image_picker_service.dart';
import '../widgets/detection_painter.dart';

/// Garbage detection screen
class DetectionScreen extends StatefulWidget {
  const DetectionScreen({super.key});

  @override
  State<DetectionScreen> createState() => _DetectionScreenState();
}

class _DetectionScreenState extends State<DetectionScreen> {
  final ImagePickerService _imagePickerService = ImagePickerService();
  final GarbageDetectorService _apiService = GarbageDetectorService();

  File? _selectedImage;
  DetectionResponse? _detectionResult;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _pickImage(ImageSource source) async {
    if (!mounted) return;

    setState(() {
      _errorMessage = null;
      _detectionResult = null;
    });

    try {
      File? image;
      if (source == ImageSource.camera) {
        image = await _imagePickerService.pickFromCamera();
      } else {
        image = await _imagePickerService.pickFromGallery();
      }

      if (image != null && mounted) {
        setState(() {
          _selectedImage = image;
        });
        await _detectGarbage(image);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
        });
      }
    }
  }

  Future<void> _detectGarbage(File image) async {
    if (!mounted) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await _apiService.detectGarbage(image);
      if (mounted) {
        setState(() {
          _detectionResult = result;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Garbage Detection'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Image display area
              if (_selectedImage != null)
                Card(
                  elevation: 4,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: _detectionResult != null
                        ? DetectionOverlay(
                            detections: _detectionResult!.detections,
                            imageSize: _getImageSize(),
                            child: Image.file(_selectedImage!),
                          )
                        : Image.file(_selectedImage!),
                  ),
                )
              else
                Container(
                  height: 300,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.image, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text(
                          'No image selected',
                          style: TextStyle(color: Colors.grey, fontSize: 16),
                        ),
                      ],
                    ),
                  ),
                ),

              const SizedBox(height: 24),

              // Action buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _isLoading ? null : () => _pickImage(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt),
                      label: const Text('Take Photo'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _isLoading ? null : () => _pickImage(ImageSource.gallery),
                      icon: const Icon(Icons.photo_library),
                      label: const Text('From Gallery'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                        backgroundColor: Colors.blue,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Loading indicator
              if (_isLoading)
                const Card(
                  child: Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Column(
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 16),
                        Text('Analyzing image...', style: TextStyle(fontSize: 16)),
                      ],
                    ),
                  ),
                ),

              // Error message
              if (_errorMessage != null)
                Card(
                  color: Colors.red[50],
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        const Icon(Icons.error, color: Colors.red),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(color: Colors.red),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

              // Detection results
              if (_detectionResult != null && !_isLoading)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Detection Results',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const Divider(),
                        Text(
                          'Found ${_detectionResult!.detectionCount} item(s)',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        Text(
                          'Processing time: ${_detectionResult!.inferenceTimeMs.toStringAsFixed(2)}ms',
                          style: const TextStyle(color: Colors.grey),
                        ),
                        const SizedBox(height: 16),
                        ..._detectionResult!.detections.map((detection) {
                          return Card(
                            color: Colors.green[50],
                            child: ListTile(
                              leading: const Icon(Icons.check_circle, color: Colors.green),
                              title: Text(
                                detection.specificName,
                                style: const TextStyle(fontWeight: FontWeight.bold),
                              ),
                              subtitle: Text(
                                'Confidence: ${(detection.confidence * 100).toStringAsFixed(1)}%',
                              ),
                            ),
                          );
                        }).toList(),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Size _getImageSize() {
    if (_selectedImage == null) return const Size(100, 100);
    try {
      final image = Image.file(_selectedImage!).image;
      return const Size(100, 100);
    } catch (e) {
      return const Size(100, 100);
    }
  }
}

enum ImageSource { camera, gallery }
