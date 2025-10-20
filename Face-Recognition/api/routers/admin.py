from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import StudentCreate, StudentResponse, TeacherCreate, TeacherResponse, ClassCreate
from models import Student, Teacher
from routers.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Student management
@router.get("/students")
def get_students(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Get all students"""
    students = db.query(Student).all()
    return students

@router.post("/students", response_model=StudentResponse)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Create student profile"""
    if student_data.year and (student_data.year < 2000 or student_data.year > 2100):
        raise HTTPException(status_code=400, detail="Year must be between 2000 and 2100")

    last_student = db.query(Student).order_by(Student.id.desc()).first()
    next_number = 1 if not last_student else last_student.id + 1
    student_code = f"SV{next_number:03d}"

    student = Student(
        student_code=student_code,
        full_name=student_data.full_name,
        email=student_data.email,
        phone=student_data.phone,
        year=student_data.year
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return student

@router.post("/students/{student_id}/face-data")
async def upload_face_data(student_id: int, data: dict, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    import base64
    import os
    from pathlib import Path
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student_dir = Path(f"../Dataset/FaceData/raw/{student.student_code}")
    student_dir.mkdir(parents=True, exist_ok=True)
    existing_files = list(student_dir.glob("*.jpg"))
    next_index = len(existing_files) + 1
    image_data = base64.b64decode(data["image_base64"])
    image_path = student_dir / f"{next_index}.jpg"
    with open(image_path, "wb") as f:
        f.write(image_data)
    return {"message": "Image uploaded", "path": str(image_path)}

# Teacher management
@router.get("/teachers")
def get_all_teachers(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Get all teachers"""
    teachers = db.query(Teacher).all()
    return teachers

@router.post("/teachers", response_model=TeacherResponse)
def create_teacher(teacher_data: TeacherCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Create teacher profile"""
    last_teacher = db.query(Teacher).order_by(Teacher.id.desc()).first()
    next_number = 1 if not last_teacher else last_teacher.id + 1
    teacher_code = f"GV{next_number:03d}"

    teacher = Teacher(
        teacher_code=teacher_code,
        full_name=teacher_data.full_name,
        email=teacher_data.email,
        phone=teacher_data.phone,
        department=teacher_data.department
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher

# Get all classes
@router.get("/classes")
def get_all_classes(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    from models import Class
    classes = db.query(Class).all()
    return classes

@router.post("/classes")
def create_class(class_data: ClassCreate, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    from models import Class
    teacher = db.query(Teacher).filter(Teacher.id == class_data.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    last_class = db.query(Class).order_by(Class.id.desc()).first()
    next_number = 1 if not last_class else last_class.id + 1
    class_code = f"LOP{next_number:03d}"

    new_class = Class(
        class_code=class_code,
        class_name=class_data.class_name,
        teacher_id=class_data.teacher_id,
        semester=class_data.semester,
        year=class_data.year
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

@router.put("/classes/{class_id}")
def update_class(class_id: int, class_data: dict, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    from models import Class
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    cls.class_code = class_data["class_code"]
    cls.class_name = class_data["class_name"]
    db.commit()
    db.refresh(cls)
    return cls

@router.delete("/classes/{class_id}")
def delete_class(class_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    from models import Class
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    db.delete(cls)
    db.commit()
    return {"message": "Class deleted"}

@router.post("/classes/{class_id}/students/{student_id}")
def add_student_to_class(class_id: int, student_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Add student to class"""
    from models import Class, ClassStudent

    # Check if class exists
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Check if already added
    existing = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == student_id
    ).first()
    if existing:
        return {"message": "Student already in class"}

    # Add student to class
    class_student = ClassStudent(class_id=class_id, student_id=student_id)
    db.add(class_student)
    db.commit()

    return {"message": "Student added to class"}

# Attendance management
@router.get("/attendance/sessions")
def get_all_sessions(db: Session = Depends(get_db), _admin = Depends(require_admin)):
    from models import AttendanceSession
    sessions = db.query(AttendanceSession).all()
    return sessions

@router.get("/attendance/sessions/{session_id}/summary")
def get_session_summary(session_id: int, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    from models import AttendanceSession, AttendanceRecord, ClassStudent
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    total_students = db.query(ClassStudent).filter(ClassStudent.class_id == session.class_id).count()
    present_count = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_id,
        AttendanceRecord.status == "present"
    ).count()
    return {
        "total_students": total_students,
        "present_count": present_count,
        "absent_count": total_students - present_count
    }

# Train model
@router.post("/train-model")
async def train_model(_admin = Depends(require_admin)):
    """Train face recognition model (admin only)"""
    from services.training import training_service
    import asyncio

    # Run training and wait for completion
    loop = asyncio.get_event_loop()
    success, message = await loop.run_in_executor(None, training_service.train_model)

    if success:
        # Reload face recognition service
        from services.face_recognition import face_recognition_service
        face_recognition_service.model_loaded = False

    return {"success": success, "message": message}
