// import 'dart:io';
// import 'package:dio/dio.dart';
// import '../models/detection.dart';

// /// Garbage detection API service
// class GarbageDetectorService {
//   // Use 10.0.2.2 for Android emulator to access localhost API
//   static const String defaultApiUrl = "http://10.0.2.2:8000";

//   late final Dio _dio;
//   final String apiUrl;

//   GarbageDetectorService({String? apiUrl})
//       : apiUrl = apiUrl ?? defaultApiUrl {
//     _dio = Dio(BaseOptions(
//       baseUrl: this.apiUrl,
//       connectTimeout: const Duration(seconds: 30),
//       receiveTimeout: const Duration(seconds: 300), // Increased for CPU inference
//       sendTimeout: const Duration(seconds: 60),
//     ));
//   }

//   /// Check API health status
//   Future<bool> checkHealth() async {
//     try {
//       final response = await _dio.get('/health');
//       return response.statusCode == 200;
//     } catch (e) {
//       return false;
//     }
//   }

//   /// Detect garbage in image
//   Future<DetectionResponse> detectGarbage(File imageFile) async {
//     try {
//       final formData = FormData.fromMap({
//         'image': await MultipartFile.fromFile(
//           imageFile.path,
//           filename: imageFile.path.split('/').last,
//         ),
//       });

//       final response = await _dio.post(
//         '/v1/detect_trash',
//         data: formData,
//       );

//       if (response.statusCode == 200) {
//         return DetectionResponse.fromJson(response.data);
//       } else {
//         throw Exception('Detection failed: ${response.statusCode}');
//       }
//     } on DioException catch (e) {
//       if (e.type == DioExceptionType.connectionTimeout) {
//         throw Exception('Connection timeout. Please check your network.');
//       } else if (e.type == DioExceptionType.receiveTimeout) {
//         throw Exception('Request timeout. Please try again.');
//       } else if (e.response != null) {
//         throw Exception('API error: ${e.response?.statusCode}');
//       } else {
//         throw Exception('Network error. Please check your connection.');
//       }
//     } catch (e) {
//       throw Exception('Unexpected error: $e');
//     }
//   }

//   /// Get garbage categories information
//   Future<List<dynamic>> getCategories() async {
//     try {
//       final response = await _dio.get('/v1/categories');
//       if (response.statusCode == 200) {
//         return response.data as List<dynamic>;
//       } else {
//         throw Exception('Failed to get categories');
//       }
//     } catch (e) {
//       throw Exception('Error fetching categories: $e');
//     }
//   }
// }

import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path/path.dart';

import '../models/detection.dart';

class GarbageDetectorService {
  late final Dio _dio;

  // For Android emulator, this IP points to your computer's localhost.
  // This is confirmed to be correct from our previous discussion.
  final String _apiUrl = "http://10.0.2.2:8000";

  GarbageDetectorService() {
    final options = BaseOptions(
      baseUrl: _apiUrl,
      // Timeout for establishing a connection (e.g., 30 seconds)
      connectTimeout: const Duration(seconds: 30),
      // Timeout for receiving data. We increase this to 3 minutes.
      receiveTimeout: const Duration(seconds: 180),
      // Timeout for sending data (e.g., 60 seconds)
      sendTimeout: const Duration(seconds: 60),
    );
    _dio = Dio(options);
  }

  /// Uploads an image to the API and returns the detection results.
  /// This function now includes robust error handling.
  Future<DetectionResponse> detectGarbage(File imageFile) async {
    final String fileName = basename(imageFile.path);
    final formData = FormData.fromMap({
      'image': await MultipartFile.fromFile(imageFile.path, filename: fileName),
    });

    try {
      final response = await _dio.post('/v1/detect_trash', data: formData);

      if (response.statusCode == 200) {
        return DetectionResponse.fromJson(response.data);
      } else {
        throw Exception('Server returned an error: ${response.statusCode} ${response.statusMessage}');
      }
    } on DioException catch (e, stackTrace) {
      // This block is specifically for Dio network errors and provides the most detail.
      print("🔥🔥🔥 DioException Caught (网络错误) 🔥🔥🔥");
      print("Error Type: ${e.type}");
      print("Error Message: ${e.message}");
      print("Request Path: ${e.requestOptions.path}");
      if (e.response != null) {
        print("Response Data: ${e.response?.data}");
        print("Response Status: ${e.response?.statusCode}");
      }
      print("Stack Trace: $stackTrace");
      throw Exception('API call failed with DioException. Check the debug console for details.');

    } catch (e, stackTrace) {
      // This is a general catch block for all other unexpected errors.
      print("🔥🔥🔥 General Exception Caught (通用错误) 🔥🔥🔥");
      print("Error Type: ${e.runtimeType}");
      print("Error Object: $e");
      print("Stack Trace: $stackTrace");
      throw Exception('An unexpected error occurred. Check the debug console for details.');
    }
  }
}

