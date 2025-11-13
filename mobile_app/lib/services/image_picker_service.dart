import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';

/// Image picker service with permission handling
class ImagePickerService {
  final ImagePicker _picker = ImagePicker();

  /// Pick image from camera
  Future<File?> pickFromCamera() async {
    // Request camera permission
    final cameraStatus = await Permission.camera.request();

    if (!cameraStatus.isGranted) {
      throw Exception('Camera permission denied');
    }

    final XFile? image = await _picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1920,
      imageQuality: 85,
    );

    return image != null ? File(image.path) : null;
  }

  /// Pick image from gallery
  Future<File?> pickFromGallery() async {
    // Request storage permission
    final storageStatus = await Permission.photos.request();

    if (!storageStatus.isGranted) {
      throw Exception('Storage permission denied');
    }

    final XFile? image = await _picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1920,
      imageQuality: 85,
    );

    return image != null ? File(image.path) : null;
  }

  /// Check if camera permission is granted
  Future<bool> isCameraPermissionGranted() async {
    return await Permission.camera.isGranted;
  }

  /// Check if storage permission is granted
  Future<bool> isStoragePermissionGranted() async {
    return await Permission.photos.isGranted;
  }

  /// Open app settings
  Future<void> openAppSettings() async {
    await openAppSettings();
  }
}
