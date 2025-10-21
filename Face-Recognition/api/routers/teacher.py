from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date, time
import os
import shutil

from database import get_db
from models import User, Teacher, Class, Student, ClassStudent, AttendanceSession, AttendanceRecord
from routers.auth import require_teacher

router = APIRouter(prefix="/api/teacher", tags=["teacher"])

class ClassInfo(BaseModel):
    class_id: int
    class_code: str
    class_name: str
    subject_code: str
    subject_name: str
    credits: int
    semester: str
    year: int
    student_count: int
    schedules: List[dict]

class StudentInfo(BaseModel):
    student_id: int
    student_code: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    year: Optional[int]
    has_face_data: bool

class AddStudentsRequest(BaseModel):
    student_ids: List[int]

class FaceImageInfo(BaseModel):
    image_path: str
    created_at: Optional[str]

class AttendanceInfo(BaseModel):
    student_id: int
    student_code: str
    full_name: str
    check_in_time: Optional[datetime]
    status: str
    confidence: Optional[float]

@router.get("/students", response_model=List[StudentInfo])
def get_all_students(user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    """Get all students (for adding to class)"""
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    students = db.query(Student).all()
    result = []
    for student in students:
        # Check if student has face data
        face_data_path = f"Dataset/FaceData/processed/{student.student_code}"
        has_face_data = os.path.exists(face_data_path) and len(os.listdir(face_data_path)) > 0

        result.append(StudentInfo(
            student_id=student.id,
            student_code=student.student_code,
            full_name=student.full_name,
            email=student.email,
            phone=student.phone,
            year=student.year,
            has_face_data=has_face_data
        ))

    return result

@router.get("/my-classes", response_model=List[ClassInfo])
def get_my_classes(user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    classes = db.query(Class).filter(Class.teacher_id == user.teacher.id).all()

    result = []
    for cls in classes:
        student_count = db.query(ClassStudent).filter(ClassStudent.class_id == cls.id).count()

        schedules = []
        for schedule in cls.schedules:
            schedules.append({
                "day_of_week": schedule.day_of_week,
                "start_time": str(schedule.start_time),
                "end_time": str(schedule.end_time),
                "room": schedule.room,
                "mode": schedule.mode
            })

        result.append(ClassInfo(
            class_id=cls.id,
            class_code=cls.class_code,
            class_name=cls.class_name,
            subject_code=cls.subject.subject_code,
            subject_name=cls.subject.subject_name,
            credits=cls.subject.credits,
            semester=cls.semester,
            year=cls.year,
            student_count=student_count,
            schedules=schedules
        ))

    return result

@router.get("/classes/{class_id}/students", response_model=List[StudentInfo])
def get_class_students(class_id: int, user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    enrollments = db.query(ClassStudent).filter(ClassStudent.class_id == class_id).all()

    result = []
    for enrollment in enrollments:
        student = enrollment.student

        face_data_path = os.path.join("Dataset", "FaceData", "processed", student.student_code)
        has_face_data = os.path.exists(face_data_path) and len(os.listdir(face_data_path)) > 0

        result.append(StudentInfo(
            student_id=student.id,
            student_code=student.student_code,
            full_name=student.full_name,
            email=student.email,
            phone=student.phone,
            year=student.year,
            has_face_data=has_face_data
        ))

    return result

@router.post("/classes/{class_id}/students")
def add_students_to_class(class_id: int, request: AddStudentsRequest, user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    added_count = 0
    for student_id in request.student_ids:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            continue

        existing = db.query(ClassStudent).filter(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == student_id
        ).first()

        if not existing:
            enrollment = ClassStudent(class_id=class_id, student_id=student_id)
            db.add(enrollment)
            added_count += 1

    db.commit()

    return {"message": f"Added {added_count} students to class", "added_count": added_count}

@router.delete("/classes/{class_id}/students/{student_id}")
def remove_student_from_class(class_id: int, student_id: int, user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    enrollment = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == student_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not enrolled in this class")

    db.delete(enrollment)
    db.commit()

    return {"message": "Student removed from class"}

@router.get("/students/{student_id}/face-images", response_model=List[FaceImageInfo])
def get_student_face_images(student_id: int, user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    enrolled_classes = db.query(ClassStudent).filter(
        ClassStudent.student_id == student_id,
        ClassStudent.class_id.in_(
            db.query(Class.id).filter(Class.teacher_id == user.teacher.id)
        )
    ).first()

    if not enrolled_classes:
        raise HTTPException(status_code=403, detail="Student not in any of your classes")

    face_data_path = os.path.join("Dataset", "FaceData", "processed", student.student_code)

    if not os.path.exists(face_data_path):
        return []

    images = []
    for filename in os.listdir(face_data_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(face_data_path, filename)
            created_at = datetime.fromtimestamp(os.path.getctime(image_path)).isoformat()
            images.append(FaceImageInfo(
                image_path=image_path,
                created_at=created_at
            ))

    return images

@router.delete("/students/{student_id}/face-images")
def delete_student_face_images(student_id: int, user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    enrolled_classes = db.query(ClassStudent).filter(
        ClassStudent.student_id == student_id,
        ClassStudent.class_id.in_(
            db.query(Class.id).filter(Class.teacher_id == user.teacher.id)
        )
    ).first()

    if not enrolled_classes:
        raise HTTPException(status_code=403, detail="Student not in any of your classes")

    face_data_path = os.path.join("Dataset", "FaceData", "processed", student.student_code)

    if not os.path.exists(face_data_path):
        return {"message": "No face images found", "deleted_count": 0}

    deleted_count = len(os.listdir(face_data_path))
    shutil.rmtree(face_data_path)

    return {"message": f"Deleted {deleted_count} face images", "deleted_count": deleted_count}

@router.get("/classes/{class_id}/attendance", response_model=List[AttendanceInfo])
def get_class_attendance(
    class_id: int,
    attendance_date: Optional[date] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    if not attendance_date:
        attendance_date = date.today()

    # Parse time parameters if provided
    session_start = None
    session_end = None
    if start_time and end_time:
        try:
            session_start = time.fromisoformat(start_time)
            session_end = time.fromisoformat(end_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM:SS")

    enrollments = db.query(ClassStudent).filter(ClassStudent.class_id == class_id).all()

    result = []
    for enrollment in enrollments:
        student = enrollment.student

        # Build query with optional time filter
        query = db.query(AttendanceRecord).join(AttendanceSession).filter(
            AttendanceSession.class_id == class_id,
            AttendanceRecord.student_id == student.id,
            AttendanceSession.session_date == attendance_date
        )

        # Add time filter if provided
        if session_start and session_end:
            query = query.filter(
                AttendanceSession.start_time == session_start,
                AttendanceSession.end_time == session_end
            )

        attendance_record = query.first()

        if attendance_record:
            result.append(AttendanceInfo(
                student_id=student.id,
                student_code=student.student_code,
                full_name=student.full_name,
                check_in_time=attendance_record.check_in_time,
                status=attendance_record.status,
                confidence=attendance_record.confidence
            ))
        else:
            result.append(AttendanceInfo(
                student_id=student.id,
                student_code=student.student_code,
                full_name=student.full_name,
                check_in_time=None,
                status="absent",
                confidence=None
            ))

    return result

class ManualAttendanceRequest(BaseModel):
    student_id: int
    status: str
    start_time: Optional[str] = None  # Format: "HH:MM:SS"
    end_time: Optional[str] = None    # Format: "HH:MM:SS"

class StudentCreateRequest(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    year: Optional[int] = None
    password: str

class StudentUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    year: Optional[int] = None

@router.post("/classes/{class_id}/attendance/manual")
def mark_manual_attendance(
    class_id: int,
    request: ManualAttendanceRequest,
    user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    enrollment = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == request.student_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not enrolled in this class")

    if request.status not in ["present", "late", "absent"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be: present, late, or absent")

    today = date.today()

    # Parse start_time and end_time if provided
    if request.start_time and request.end_time:
        try:
            session_start = time.fromisoformat(request.start_time)
            session_end = time.fromisoformat(request.end_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM:SS")

        # Find session by date and time range
        session = db.query(AttendanceSession).filter(
            AttendanceSession.class_id == class_id,
            AttendanceSession.session_date == today,
            AttendanceSession.start_time == session_start,
            AttendanceSession.end_time == session_end
        ).first()
    else:
        # Fallback: find any session for today
        session = db.query(AttendanceSession).filter(
            AttendanceSession.class_id == class_id,
            func.date(AttendanceSession.created_at) == today
        ).first()
        session_start = datetime.now().time()
        session_end = datetime.now().time()

    if not session:
        session = AttendanceSession(
            class_id=class_id,
            session_date=today,
            start_time=session_start,
            end_time=session_end,
            created_by=user.id
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session.id,
        AttendanceRecord.student_id == request.student_id
    ).first()

    if existing_record:
        existing_record.status = request.status
        existing_record.check_in_time = datetime.now()
        db.commit()
        return {"message": "Attendance updated", "status": request.status}
    else:
        record = AttendanceRecord(
            session_id=session.id,
            student_id=request.student_id,
            status=request.status,
            check_in_time=datetime.now(),
            confidence=None
        )
        db.add(record)
        db.commit()
        return {"message": "Attendance marked", "status": request.status}

@router.post("/classes/{class_id}/students/new")
def create_and_add_student(
    class_id: int,
    student_data: StudentCreateRequest,
    user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    last_student = db.query(Student).order_by(Student.id.desc()).first()
    next_number = 1 if not last_student else last_student.id + 1
    student_code = f"SV{next_number:03d}"

    student = Student(
        student_code=student_code,
        full_name=student_data.full_name,
        email=student_data.email,
        phone=student_data.phone,
        year=student_data.year,
        password=student_data.password
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    user_account = User(
        username=student.student_code,
        password=student_data.password,
        role="student",
        student_id=student.id
    )
    db.add(user_account)

    enrollment = ClassStudent(
        class_id=class_id,
        student_id=student.id
    )
    db.add(enrollment)
    db.commit()

    return {
        "student_id": student.id,
        "student_code": student.student_code,
        "full_name": student.full_name,
        "message": "Student added to class successfully"
    }

@router.put("/classes/{class_id}/students/{student_id}")
def update_student_in_class(
    class_id: int,
    student_id: int,
    student_data: StudentUpdateRequest,
    user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    enrollment = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == student_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not found in this class")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student_data.full_name is not None:
        student.full_name = student_data.full_name
    if student_data.email is not None:
        student.email = student_data.email
    if student_data.phone is not None:
        student.phone = student_data.phone
    if student_data.year is not None:
        student.year = student_data.year

    db.commit()
    db.refresh(student)

    return {
        "student_id": student.id,
        "student_code": student.student_code,
        "full_name": student.full_name,
        "email": student.email,
        "phone": student.phone,
        "year": student.year,
        "message": "Student updated successfully"
    }

@router.delete("/classes/{class_id}/students/{student_id}")
def remove_student_from_class(
    class_id: int,
    student_id: int,
    user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    enrollment = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == student_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not found in this class")

    db.delete(enrollment)
    db.commit()

    return {"message": "Student removed from class successfully"}

@router.get("/classes/{class_id}/students/{student_id}/images")
def get_student_images(
    class_id: int,
    student_id: int,
    user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    if not user.teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == user.teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or you don't have permission")

    enrollment = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == student_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not found in this class")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    face_data_path = f"../Dataset/FaceData/processed/{student.student_code}"
    if not os.path.exists(face_data_path):
        return {"student_code": student.student_code, "images": []}

    images = []
    for filename in os.listdir(face_data_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(face_data_path, filename)
            stat = os.stat(image_path)
            images.append({
                "filename": filename,
                "path": image_path,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })

    return {
        "student_code": student.student_code,
        "full_name": student.full_name,
        "images": images
    }

