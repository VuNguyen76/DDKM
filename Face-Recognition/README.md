# Face Recognition Attendance System

Hệ thống điểm danh bằng nhận diện khuôn mặt cho trường Đại học Thủy Lợi (TLU).

##  Mục lục

- [Tính năng](#tính-năng)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cài đặt](#cài-đặt)
- [Chạy ứng dụng](#chạy-ứng-dụng)
- [Chạy với Docker](#chạy-với-docker)
- [Tài khoản mặc định](#tài-khoản-mặc-định)
- [API Documentation](#api-documentation)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Troubleshooting](#troubleshooting)

##  Tính năng

### Admin
- Quản lý sinh viên, giáo viên, môn học, lớp học
- Xem thống kê tổng quan
- Quản lý lịch học và điểm danh

### Giáo viên
- Xem danh sách lớp học được phân công
- Điểm danh thủ công hoặc bằng nhận diện khuôn mặt
- Quản lý sinh viên trong lớp
- Xem lịch giảng dạy theo ngày

### Sinh viên
- Xem lịch học
- Xem lịch sử điểm danh
- Cập nhật ảnh khuôn mặt cho hệ thống nhận diện

##  Công nghệ sử dụng

### Backend
- **FastAPI** - Python REST API framework
- **SQLAlchemy** - ORM cho MySQL
- **MySQL** - Database (Railway cloud)
- **MTCNN** - Face detection
- **FaceNet** - Face recognition
- **SVM** - Classification

### Frontend
- **Flutter** - Cross-platform mobile framework
- **Dart** - Programming language
- **Material Design 3** - UI design system

##  Cài đặt

### Yêu cầu hệ thống
- Python 3.11+
- Flutter SDK 3.0+
- MySQL 8.0+ (hoặc sử dụng Railway cloud)
- Android Studio / Xcode (cho mobile development)
- Docker & Docker Compose (optional)

### 1. Clone repository
```bash
git clone <repository-url>
cd Face-Recognition
```

### 2. Cài đặt Backend

#### Cài đặt Python dependencies
```bash
cd api
pip install -r requirements.txt
```

#### Cấu hình database
Tạo file `api/.env`:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/face_recognition
SECRET_KEY=your-secret-key-change-this-in-production
SESSION_TIMEOUT_HOURS=24
```

#### Khởi tạo database
```bash
python init_db.py
python seed_data.py
```

### 3. Cài đặt Flutter

```bash
cd face_recognition_app
flutter pub get
```

##  Chạy ứng dụng

### Cách 1: Sử dụng script (Windows)

#### Chạy Backend
```bash
run_backend.bat
```

#### Chạy Flutter (terminal mới)
```bash
run_flutter.bat
```

### Cách 2: Chạy thủ công

#### Chạy Backend
```bash
cd api
uvicorn main:app --reload --port 8000
```

Backend sẽ chạy tại: http://localhost:8000

API Documentation: http://localhost:8000/docs

#### Chạy Flutter
```bash
cd face_recognition_app
flutter run
```

Hoặc chỉ định device cụ thể:
```bash
flutter run -d emulator-5554
```

##  Chạy với Docker

### Build và chạy
```bash
docker-compose up --build
```

### Chỉ chạy (đã build trước đó)
```bash
docker-compose up
```

### Dừng container
```bash
docker-compose down
```

Backend trong Docker sẽ chạy tại: http://localhost:8000

**Lưu ý:** Database sẽ tự động được seed với dữ liệu mẫu khi container khởi động lần đầu.

##  Tài khoản mặc định

### Admin
- Username: `admin`
- Password: `admin`

### Giáo viên
- Username: `GV001`
- Password: `newteacher123`

### Sinh viên
- Username: `SV001`
- Password: `newstudent123`

##  API Documentation

### Authentication
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/logout` - Đăng xuất

### Admin Endpoints
- `GET /api/admin/stats` - Thống kê tổng quan
- `GET /api/admin/students` - Danh sách sinh viên
- `POST /api/admin/students` - Tạo sinh viên mới
- `GET /api/admin/teachers` - Danh sách giáo viên
- `POST /api/admin/teachers` - Tạo giáo viên mới
- `GET /api/admin/subjects` - Danh sách môn học
- `POST /api/admin/subjects` - Tạo môn học mới
- `GET /api/admin/classes` - Danh sách lớp học
- `POST /api/admin/classes` - Tạo lớp học mới

### Teacher Endpoints
- `GET /api/teacher/my-classes` - Danh sách lớp được phân công
- `GET /api/teacher/classes/{class_id}/students` - Danh sách sinh viên trong lớp
- `GET /api/teacher/students` - Danh sách tất cả sinh viên (để thêm vào lớp)
- `POST /api/teacher/classes/{class_id}/students` - Thêm sinh viên vào lớp
- `GET /api/teacher/attendance-sessions` - Danh sách buổi điểm danh
- `POST /api/teacher/attendance-sessions` - Tạo buổi điểm danh mới
- `POST /api/teacher/attendance` - Điểm danh thủ công

### Student Endpoints
- `GET /api/student/my-classes` - Danh sách lớp đang học
- `GET /api/student/my-attendance` - Lịch sử điểm danh
- `GET /api/student/profile` - Thông tin cá nhân

### Face Recognition Endpoints
- `POST /api/face/upload-images` - Upload ảnh khuôn mặt
- `POST /api/face/train` - Train model nhận diện
- `POST /api/face/recognize` - Nhận diện khuôn mặt

##  Cấu trúc thư mục

```
Face-Recognition/
 api/                        # Backend FastAPI
    routers/               # API routes
    models.py              # Database models
    database.py            # Database connection
    main.py                # FastAPI app
    requirements.txt       # Python dependencies
    seed_data.py           # Database seeding script
    .env                   # Environment variables
 face_recognition_app/      # Flutter mobile app
    lib/
       pages/            # UI screens
       widgets/          # Reusable widgets
       main.dart         # App entry point
    pubspec.yaml          # Flutter dependencies
 src/                       # Face recognition source code
 Models/                    # Trained models
 Dataset/                   # Face images dataset
 Dockerfile                 # Docker image definition
 docker-compose.yml         # Docker compose config
 entrypoint.sh             # Docker entrypoint script
 run_backend.bat           # Script chạy backend (Windows)
 run_flutter.bat           # Script chạy Flutter (Windows)
 README.md                 # This file
```

##  Troubleshooting

### Backend không kết nối được database
- Kiểm tra file `.env` có đúng thông tin database
- Kiểm tra MySQL server đang chạy
- Kiểm tra firewall không block port 3306

### Flutter không kết nối được backend
- Kiểm tra backend đang chạy tại http://localhost:8000
- Kiểm tra file `lib/constants/api_constants.dart` có đúng base URL
- Nếu chạy trên emulator Android, sử dụng `10.0.2.2` thay vì `localhost`

### Docker container không khởi động
- Kiểm tra Docker Desktop đang chạy
- Kiểm tra port 8000 không bị chiếm bởi process khác
- Xem logs: `docker-compose logs -f`

##  License

MIT License

##  Contributors

- Đại học Thủy Lợi (TLU)
