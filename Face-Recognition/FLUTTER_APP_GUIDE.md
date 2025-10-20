# Flutter App - Hướng dẫn sử dụng

## Tổng quan

Ứng dụng Flutter đã được tạo với 4 trang chính:

1. **Login Page** - Trang đăng nhập
2. **Dashboard Page** - Trang tổng quan
3. **Face Capture Page** - Trang chụp ảnh khuôn mặt
4. **Attendance Page** - Trang điểm danh

## Cấu trúc thư mục

```
face_recognition_app/
├── lib/
│   ├── constants/
│   │   └── api_constants.dart          # API endpoints configuration
│   ├── models/
│   │   ├── student.dart                # Student data model
│   │   ├── teacher.dart                # Teacher data model
│   │   ├── class_model.dart            # Class data model
│   │   └── recognition_result.dart     # Recognition result model
│   ├── services/
│   │   ├── auth_service.dart           # Authentication service
│   │   └── api_service.dart            # API communication service
│   ├── pages/
│   │   ├── login_page.dart             # Login page UI
│   │   ├── dashboard_page.dart         # Dashboard page UI
│   │   ├── face_capture_page.dart      # Face capture page UI
│   │   └── attendance_page.dart        # Attendance page UI
│   └── main.dart                       # App entry point
├── android/                            # Android configuration
├── ios/                                # iOS configuration
├── pubspec.yaml                        # Dependencies
└── README.md                           # Documentation
```

## Dependencies đã cài đặt

```yaml
camera: ^0.10.5+5              # Camera plugin
http: ^1.1.0                   # HTTP requests
shared_preferences: ^2.2.2     # Local storage for session
image_picker: ^1.0.4           # Image picker
provider: ^6.1.1               # State management
```

## Cấu hình cần thiết

### 1. Cấu hình API URL

Mở file `lib/constants/api_constants.dart` và cập nhật base URL:

```dart
class ApiConstants {
  static const String baseUrl = 'http://localhost:8000/api';
  // Hoặc sử dụng IP của máy chạy API server
  // static const String baseUrl = 'http://192.168.1.100:8000/api';
}
```

**Lưu ý quan trọng:**
- **Android Emulator**: Sử dụng `http://10.0.2.2:8000/api` (10.0.2.2 là localhost của máy host)
- **iOS Simulator**: Sử dụng `http://localhost:8000/api`
- **Thiết bị thật**: Sử dụng IP thực của máy chạy API server (ví dụ: `http://192.168.1.100:8000/api`)

### 2. Cấu hình Permissions

#### Android

Mở file `android/app/src/main/AndroidManifest.xml` và thêm:

```xml
<manifest ...>
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.INTERNET" />
    
    <application ...>
        ...
    </application>
</manifest>
```

#### iOS

Mở file `ios/Runner/Info.plist` và thêm:

```xml
<dict>
    ...
    <key>NSCameraUsageDescription</key>
    <string>Camera is required for face recognition and attendance</string>
    ...
</dict>
```

## Chạy ứng dụng

### 1. Cài đặt dependencies

```bash
cd face_recognition_app
flutter pub get
```

### 2. Chạy API server

Trước khi chạy Flutter app, đảm bảo API server đang chạy:

```bash
cd ../api
uvicorn main:app --reload --port 8000
```

### 3. Chạy Flutter app

```bash
# Chạy trên Android
flutter run

# Chạy trên iOS
flutter run -d ios

# Chạy trên emulator cụ thể
flutter devices  # Xem danh sách devices
flutter run -d <device_id>
```

## Chi tiết các trang

### 1. Login Page

**File:** `lib/pages/login_page.dart`

**Chức năng:**
- Form đăng nhập với email và password
- Validation input
- Hiển thị loading khi đang đăng nhập
- Tự động chuyển đến Dashboard khi đăng nhập thành công
- Hiển thị thông báo lỗi nếu đăng nhập thất bại

**API sử dụng:**
- `POST /api/auth/login`

**Thông tin đăng nhập mặc định:**
- Email: `admin`
- Password: `admin`

### 2. Dashboard Page

**File:** `lib/pages/dashboard_page.dart`

**Chức năng:**
- Hiển thị thông tin user đang đăng nhập
- Thống kê tổng số:
  - Sinh viên
  - Giáo viên
  - Lớp học
- Menu điều hướng đến:
  - Trang chụp ảnh khuôn mặt
  - Trang điểm danh
- Nút refresh để cập nhật dữ liệu
- Nút logout

**API sử dụng:**
- `GET /api/admin/students`
- `GET /api/admin/teachers`
- `GET /api/admin/classes`

### 3. Face Capture Page

**File:** `lib/pages/face_capture_page.dart`

**Chức năng:**
- Camera preview real-time
- Dropdown chọn sinh viên
- Auto-capture 50 ảnh (1 ảnh/giây)
- Progress bar hiển thị tiến trình chụp
- Nút "Bắt đầu chụp" / "Dừng chụp"
- Nút "Train Model" (chỉ active khi đã chụp ít nhất 1 ảnh)

**API sử dụng:**
- `GET /api/admin/students` - Lấy danh sách sinh viên
- `POST /api/face/capture` - Gửi ảnh đã chụp
- `POST /api/face/train` - Train model

**Flow:**
1. Chọn sinh viên từ dropdown
2. Click "Bắt đầu chụp"
3. Hệ thống tự động chụp 50 ảnh (mỗi giây 1 ảnh)
4. Sau khi chụp xong, click "Train Model"
5. Đợi training hoàn tất

### 4. Attendance Page

**File:** `lib/pages/attendance_page.dart`

**Chức năng:**
- Camera preview real-time
- Tự động nhận diện khuôn mặt (mỗi 2 giây)
- Hiển thị thông tin sinh viên được nhận diện:
  - Tên sinh viên
  - Mã sinh viên
  - Ca học
  - Độ tin cậy (confidence)
- Danh sách sinh viên đã điểm danh trong session
- Nút pause/resume nhận diện
- Tự động lưu điểm danh khi nhận diện thành công

**API sử dụng:**
- `POST /api/face/recognize` - Nhận diện khuôn mặt

**Flow:**
1. Mở trang, camera tự động bật
2. Hệ thống tự động nhận diện mỗi 2 giây
3. Khi nhận diện thành công:
   - Hiển thị thông tin trên màn hình
   - Thêm vào danh sách điểm danh
   - Hiển thị notification
4. Click icon pause để tạm dừng nhận diện
5. Click icon play để tiếp tục

## Models

### Student Model

```dart
class Student {
  final int id;
  final String studentCode;
  final String fullName;
  final String? email;
  final String? phone;
  final int? year;
}
```

### Teacher Model

```dart
class Teacher {
  final int id;
  final String teacherCode;
  final String fullName;
  final String? email;
  final String? phone;
  final String? department;
}
```

### Class Model

```dart
class ClassModel {
  final int id;
  final String classCode;
  final String className;
  final int teacherId;
  final String? semester;
  final int? year;
  final Teacher? teacher;
  final int? studentCount;
}
```

### Recognition Result Model

```dart
class RecognitionResult {
  final bool recognized;
  final int? studentId;
  final String? studentCode;
  final String? studentName;
  final double? confidence;
  final int? shift;
  final String? shiftName;
  final String? message;
}
```

## Services

### AuthService

```dart
// Login
final success = await authService.login('admin', 'admin');

// Logout
await authService.logout();

// Check login status
final isLoggedIn = await authService.isLoggedIn();

// Get session ID
final sessionId = await authService.getSessionId();
```

### ApiService

```dart
// Get students
final students = await apiService.getStudents();

// Get teachers
final teachers = await apiService.getTeachers();

// Get classes
final classes = await apiService.getClasses();

// Capture image
final success = await apiService.captureImage(studentId, base64Image);

// Train model
final success = await apiService.trainModel();

// Recognize face
final result = await apiService.recognizeFace(base64Image);
```

## Troubleshooting

### 1. Camera không hoạt động

**Nguyên nhân:**
- Chưa cấp quyền camera
- Permissions chưa được khai báo trong manifest

**Giải pháp:**
1. Kiểm tra AndroidManifest.xml / Info.plist
2. Uninstall app và install lại
3. Cấp quyền camera trong Settings

### 2. Không kết nối được API

**Nguyên nhân:**
- API server chưa chạy
- URL không đúng
- Firewall chặn kết nối

**Giải pháp:**
1. Kiểm tra API server đang chạy: `curl http://localhost:8000/api/auth/login`
2. Kiểm tra URL trong `api_constants.dart`
3. Trên Android emulator, sử dụng `10.0.2.2` thay vì `localhost`
4. Trên thiết bị thật, sử dụng IP của máy chạy API server
5. Tắt firewall hoặc cho phép port 8000

### 3. Lỗi build

```bash
# Clean project
flutter clean

# Get dependencies
flutter pub get

# Rebuild
flutter run
```

### 4. Session expired

**Nguyên nhân:**
- Session đã hết hạn trên server
- Session bị xóa

**Giải pháp:**
- Đăng nhập lại

## Build Release

### Android APK

```bash
flutter build apk --release
```

File output: `build/app/outputs/flutter-apk/app-release.apk`

### iOS IPA

```bash
flutter build ios --release
```

## Tính năng chưa implement

- Quản lý sinh viên (CRUD)
- Quản lý giáo viên (CRUD)
- Quản lý lớp học (CRUD)
- Xem báo cáo điểm danh
- Xuất báo cáo
- Thông báo push notification

## Next Steps

1. Test app trên thiết bị thật
2. Thêm ảnh placeholder/logo
3. Cải thiện UI/UX
4. Thêm error handling
5. Thêm loading states
6. Implement các tính năng CRUD
7. Thêm unit tests
8. Thêm integration tests

## License

MIT License

