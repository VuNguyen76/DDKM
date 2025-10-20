import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import '../services/auth_service.dart';
import '../constants/api_constants.dart';

class FaceAttendancePage extends StatefulWidget {
  final int classId;
  final String className;

  const FaceAttendancePage({
    super.key,
    required this.classId,
    required this.className,
  });

  @override
  State<FaceAttendancePage> createState() => _FaceAttendancePageState();
}

class _FaceAttendancePageState extends State<FaceAttendancePage> {
  final _authService = AuthService();
  CameraController? _cameraController;
  List<CameraDescription>? _cameras;
  bool _isInitialized = false;
  bool _isProcessing = false;
  String? _message;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras == null || _cameras!.isEmpty) {
        setState(() {
          _message = 'Không tìm thấy camera';
        });
        return;
      }

      // Use front camera if available
      final frontCamera = _cameras!.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
        orElse: () => _cameras!.first,
      );

      _cameraController = CameraController(
        frontCamera,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _cameraController!.initialize();
      setState(() {
        _isInitialized = true;
      });
    } catch (e) {
      setState(() {
        _message = 'Lỗi khởi tạo camera: $e';
      });
    }
  }

  Future<void> _captureAndCheckIn() async {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }

    setState(() {
      _isProcessing = true;
      _message = 'Đang xử lý...';
    });

    try {
      final sessionId = await _authService.getSessionId();
      if (sessionId == null) {
        setState(() {
          _message = 'Phiên đăng nhập hết hạn';
          _isProcessing = false;
        });
        return;
      }

      // Capture image
      final XFile image = await _cameraController!.takePicture();

      // Send to server
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiConstants.baseUrl}/student/check-in'),
      );
      request.headers['session-id'] = sessionId;
      request.fields['class_id'] = widget.classId.toString();
      request.files.add(await http.MultipartFile.fromPath('image', image.path));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        final data = json.decode(responseBody);
        setState(() {
          _message = 'Điểm danh thành công!\n'
              'Trạng thái: ${data['status']}\n'
              'Độ tin cậy: ${(data['confidence'] * 100).toStringAsFixed(1)}%';
          _isProcessing = false;
        });

        // Show success dialog
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Thành công'),
            content: Text(_message!),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context); // Close dialog
                  Navigator.pop(context); // Go back to home
                },
                child: const Text('OK'),
              ),
            ],
          ),
        );
      } else {
        final error = json.decode(responseBody);
        setState(() {
          _message = 'Lỗi: ${error['detail'] ?? 'Không thể điểm danh'}';
          _isProcessing = false;
        });
      }
    } catch (e) {
      setState(() {
        _message = 'Lỗi: $e';
        _isProcessing = false;
      });
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('Điểm danh - ${widget.className}'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Expanded(
            child: _isInitialized && _cameraController != null
                ? CameraPreview(_cameraController!)
                : Center(
                    child: _message != null
                        ? Text(
                            _message!,
                            style: const TextStyle(color: Colors.white),
                          )
                        : const CircularProgressIndicator(),
                  ),
          ),
          Container(
            color: Colors.black87,
            padding: const EdgeInsets.all(20.0),
            child: Column(
              children: [
                if (_message != null && !_isProcessing)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16.0),
                    child: Text(
                      _message!,
                      style: TextStyle(
                        color: _message!.contains('thành công')
                            ? Colors.green
                            : Colors.red,
                        fontSize: 16,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _captureAndCheckIn,
                    icon: _isProcessing
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Icon(Icons.camera_alt),
                    label: Text(_isProcessing ? 'Đang xử lý...' : 'Chụp ảnh và điểm danh'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      textStyle: const TextStyle(fontSize: 18),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Hướng khuôn mặt vào camera và bấm nút để điểm danh',
                  style: TextStyle(color: Colors.white70, fontSize: 14),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

