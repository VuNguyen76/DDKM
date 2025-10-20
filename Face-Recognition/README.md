# Face Recognition Attendance System

Hệ thống điểm danh tự động bằng nhận diện khuôn mặt cho trường học.

## Tính năng

### Backend (FastAPI)
- ✅ Nhận diện khuôn mặt (MTCNN + FaceNet + SVM)
- ✅ REST API đầy đủ cho quản lý điểm danh
- ✅ Tự động sinh mã sinh viên (SV001, SV002, ...)
- ✅ Tự động sinh mã giáo viên (GV001, GV002, ...)
- ✅ Tự động sinh mã lớp (LOP001, LOP002, ...)
- ✅ Hệ thống 4 ca học trong ngày
- ✅ Xác thực đơn giản (session-based)
- ✅ Chỉ admin có thể đăng nhập

### Frontend (HTML/CSS/JavaScript)
- ✅ Trang đăng nhập
- ✅ Dashboard tổng quan
- ✅ Quản lý sinh viên
- ✅ Quản lý giáo viên
- ✅ Quản lý lớp học (gán giáo viên cho lớp)
- ✅ Chụp ảnh tự động (50 ảnh, 1 FPS)
- ✅ Nhận diện khuôn mặt real-time
- ✅ Báo cáo điểm danh

## Công nghệ

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, SQLite
- **Face Detection**: MTCNN
- **Face Recognition**: FaceNet (128-dim embeddings) + SVM
- **Deployment**: Docker, Docker Compose

## Cài đặt

### Yêu cầu

- Python 3.11+
- Docker & Docker Compose (cho deployment)
- Webcam (cho chụp ảnh và nhận diện)

### Chạy Local (Development)

1. **Clone repository**
```bash
git clone <repo-url>
cd Face-Recognition
```

2. **Cài đặt dependencies**
```bash
cd api
pip install -r requirements.txt
```

3. **Khởi tạo database**
```bash
python init_db.py
```

4. **Chạy API server**
```bash
uvicorn main:app --reload --port 8000
```

5. **Mở frontend**
- Mở file `frontend/login.html` bằng Live Server hoặc web server
- Hoặc dùng Python: `python -m http.server 3000` trong thư mục `frontend`

6. **Đăng nhập**
- Username: `admin`
- Password: `admin`

### Chạy với Docker

1. **Build và start services**
```bash
docker-compose up -d --build
```

2. **Truy cập**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: Mở `frontend/login.html` trong browser

3. **Xem logs**
```bash
docker-compose logs -f
```

4. **Stop services**
```bash
docker-compose down
```

## Hướng dẫn sử dụng

### 1. Tạo giáo viên

1. Vào trang **Dashboard**
2. Click **Quản lý lớp**
3. Trước tiên cần tạo giáo viên (nếu chưa có)
4. Nhập thông tin giáo viên
5. Hệ thống tự động sinh mã giáo viên (GV001, GV002, ...)

### 2. Tạo lớp học

1. Vào trang **Quản lý lớp**
2. Click **Thêm lớp mới**
3. Nhập tên lớp
4. Chọn giáo viên từ dropdown
5. Nhập học kỳ và năm học (tùy chọn)
6. Hệ thống tự động sinh mã lớp (LOP001, LOP002, ...)

### 3. Tạo sinh viên

1. Vào trang **Chụp ảnh**
2. Click **Thêm sinh viên mới**
3. Nhập họ tên, email, năm học
4. Hệ thống tự động sinh mã sinh viên (SV001, SV002, ...)

### 4. Chụp ảnh khuôn mặt

1. Vào trang **Chụp ảnh**
2. Chọn sinh viên từ dropdown
3. Click **Bắt đầu chụp**
4. Hệ thống tự động chụp 50 ảnh (50 giây)
5. Sau khi chụp xong, click **Train Model**

### 5. Điểm danh

1. Vào trang **Điểm danh**
2. Camera tự động bật
3. Hệ thống nhận diện khuôn mặt real-time
4. Khi nhận diện thành công, tự động lưu điểm danh
5. Hiển thị thông tin sinh viên và ca học

### 6. Xem báo cáo

1. Vào trang **Báo cáo**
2. Chọn ngày và ca học
3. Xem danh sách sinh viên đã điểm danh

## Hệ thống ca học

Hệ thống tự động phát hiện ca học dựa trên thời gian hiện tại:

- **Ca 1**: 07:00 - 10:00 (nghỉ 10:00-10:15)
- **Ca 2**: 10:15 - 13:15 (nghỉ 13:15-13:30)
- **Ca 3**: 13:30 - 16:30 (nghỉ 16:30-16:45)
- **Ca 4**: 16:45 - 19:45 (nghỉ 19:45-20:00)

## API Documentation

### Authentication

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

**Response**
```json
{
  "session_id": "uuid-string",
  "message": "Login successful"
}
```

### Students

**Get all students**
```http
GET /api/admin/students
session-id: <session_id>
```

**Create student** (auto-generate student_code)
```http
POST /api/admin/students
session-id: <session_id>
Content-Type: application/json

{
  "full_name": "Nguyen Van A",
  "email": "a@example.com",
  "year": 2024
}
```

### Teachers

**Get all teachers**
```http
GET /api/admin/teachers
session-id: <session_id>
```

**Create teacher** (auto-generate teacher_code)
```http
POST /api/admin/teachers
session-id: <session_id>
Content-Type: application/json

{
  "full_name": "Tran Thi B",
  "email": "b@example.com",
  "department": "Computer Science"
}
```

### Classes

**Get all classes**
```http
GET /api/admin/classes
session-id: <session_id>
```

**Create class** (auto-generate class_code)
```http
POST /api/admin/classes
session-id: <session_id>
Content-Type: application/json

{
  "class_name": "Web Development",
  "teacher_id": 1,
  "semester": "HK1",
  "year": 2024
}
```

### Face Recognition

**Capture face**
```http
POST /api/face/capture
Content-Type: application/json

{
  "student_id": 1,
  "image": "base64-encoded-image"
}
```

**Train model**
```http
POST /api/face/train
```

**Recognize face**
```http
POST /api/face/recognize
Content-Type: application/json

{
  "image": "base64-encoded-image"
}
```

Xem chi tiết tại: [FRONTEND_API_INTEGRATION.md](FRONTEND_API_INTEGRATION.md)

## Cấu trúc thư mục

```
Face-Recognition/
├── api/                    # Backend API
│   ├── routers/           # API routes
│   │   ├── auth.py       # Authentication
│   │   ├── admin.py      # Admin CRUD
│   │   └── face.py       # Face recognition
│   ├── services/          # Business logic
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database connection
│   ├── config.py          # Configuration
│   ├── main.py           # FastAPI app
│   └── requirements.txt   # Python dependencies
├── Dataset/              # Face images
│   └── FaceData/
│       ├── raw/         # Raw captured images
│       └── processed/   # Processed images
├── Models/              # Trained models
│   ├── svm_model.pkl   # SVM classifier
│   └── label_encoder.pkl
├── Dockerfile           # Docker image
├── docker-compose.yml   # Docker Compose config
└── README.md           # This file
```

## Tài liệu

- [FRONTEND_API_INTEGRATION.md](FRONTEND_API_INTEGRATION.md) - Hướng dẫn tích hợp API
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Hướng dẫn deploy với Docker

## Troubleshooting

### Lỗi khi train model

- Đảm bảo đã chụp đủ 50 ảnh cho mỗi sinh viên
- Kiểm tra thư mục `Dataset/FaceData/processed/` có ảnh không
- Xóa cache Python: `rm -rf api/__pycache__`

### Nhận diện không chính xác

- Tăng số lượng ảnh chụp (hiện tại: 50 ảnh)
- Đảm bảo ánh sáng tốt khi chụp
- Chụp ảnh từ nhiều góc độ khác nhau
- Train lại model sau khi chụp thêm ảnh

### CORS errors

- Kiểm tra API đang chạy trên port 8000
- Kiểm tra `API_BASE_URL` trong `frontend/js/api.js`
- Kiểm tra CORS settings trong `api/main.py`

## License

MIT License

