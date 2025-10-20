from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional, List

# Auth schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    session_id: str
    username: str

# Student schemas
class StudentCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    year: Optional[int] = None

class StudentResponse(BaseModel):
    id: int
    student_code: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    year: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# Teacher schemas
class TeacherCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None

class TeacherResponse(BaseModel):
    id: int
    teacher_code: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    department: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Class schemas
class ClassCreate(BaseModel):
    class_name: str
    teacher_id: int
    semester: Optional[str] = None
    year: Optional[int] = None

class ClassResponse(BaseModel):
    id: int
    class_code: str
    class_name: str
    semester: Optional[str]
    year: Optional[int]
    schedule: Optional[str]
    teacher: TeacherResponse
    created_at: datetime
    
    class Config:
        from_attributes = True

# Attendance Session schemas
class AttendanceSessionCreate(BaseModel):
    class_id: int
    session_date: date
    shift: str
    attendance_type: str = "face"

class AttendanceSessionResponse(BaseModel):
    id: int
    class_id: int
    session_date: date
    shift: str
    start_time: time
    end_time: time
    attendance_type: str
    created_at: datetime

    class Config:
        from_attributes = True

# Attendance Record schemas
class AttendanceRecordCreate(BaseModel):
    session_id: int
    student_id: int
    status: str = "present"
    confidence: Optional[float] = None

class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    student: StudentResponse
    check_in_time: datetime
    status: str
    confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

# Attendance Summary schema
class AttendanceSummary(BaseModel):
    total_students: int
    present_count: int
    absent_count: int
    late_count: int
    present_students: List[StudentResponse]
    absent_students: List[StudentResponse]
    late_students: List[StudentResponse]

# Face Recognition schemas
class FaceRecognitionRequest(BaseModel):
    image_base64: str

class FaceRecognitionResponse(BaseModel):
    success: bool
    student_name: Optional[str] = None
    student_code: Optional[str] = None
    confidence: Optional[float] = None
    message: str

