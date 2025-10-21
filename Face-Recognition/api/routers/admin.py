from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from database import get_db
from models import Student, Teacher, Subject, Class, ClassSchedule, ClassStudent, User
from routers.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class StudentCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    year: Optional[int] = None
    password: str

class TeacherCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    password: str

class SubjectCreate(BaseModel):
    subject_name: str
    credits: int

class ClassCreate(BaseModel):
    class_name: str
    subject_id: int
    teacher_id: int
    semester: str
    year: int

class ClassScheduleCreate(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    room: str
    mode: str = "offline"

# Statistics
@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _admin = Depends(require_admin)):
    """Get system statistics"""
    total_students = db.query(Student).count()
    total_teachers = db.query(Teacher).count()
    total_classes = db.query(Class).count()
    total_subjects = db.query(Subject).count()

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_classes": total_classes,
        "total_subjects": total_subjects
    }

# Student management
@router.get("/students")
def get_students(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """Get all students"""
    students = db.query(Student).all()
    return students

@router.post("/students")
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
        year=student_data.year,
        password=student_data.password
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    user = User(
        username=student.student_code,
        password=student_data.password,
        role="student",
        student_id=student.id
    )
    db.add(user)
    db.commit()

    return student

@router.put("/students/{student_id}")
def update_student(student_id: int, student_data: StudentCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.full_name = student_data.full_name
    if student_data.email:
        student.email = student_data.email
    if student_data.phone:
        student.phone = student_data.phone
    if student_data.year:
        student.year = student_data.year
    if student_data.password:
        student.password = student_data.password
        user = db.query(User).filter(User.student_id == student.id).first()
        if user:
            user.password = student_data.password

    db.commit()
    db.refresh(student)
    return student

@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    user = db.query(User).filter(User.student_id == student.id).first()
    if user:
        db.delete(user)

    db.delete(student)
    db.commit()
    return {"message": "Student deleted"}

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

@router.post("/teachers")
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
        department=teacher_data.department,
        password=teacher_data.password
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    user = User(
        username=teacher.teacher_code,
        password=teacher_data.password,
        role="teacher",
        teacher_id=teacher.id
    )
    db.add(user)
    db.commit()

    return teacher

@router.put("/teachers/{teacher_id}")
def update_teacher(teacher_id: int, teacher_data: TeacherCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.full_name = teacher_data.full_name
    if teacher_data.email:
        teacher.email = teacher_data.email
    if teacher_data.phone:
        teacher.phone = teacher_data.phone
    if teacher_data.department:
        teacher.department = teacher_data.department
    if teacher_data.password:
        teacher.password = teacher_data.password
        user = db.query(User).filter(User.teacher_id == teacher.id).first()
        if user:
            user.password = teacher_data.password

    db.commit()
    db.refresh(teacher)
    return teacher

@router.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    user = db.query(User).filter(User.teacher_id == teacher.id).first()
    if user:
        db.delete(user)

    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted"}

# Get all classes
@router.get("/classes")
def get_all_classes(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    from models import Class
    classes = db.query(Class).all()
    result = []
    for cls in classes:
        result.append({
            "id": cls.id,
            "class_code": cls.class_code,
            "class_name": cls.class_name,
            "subject_id": cls.subject_id,
            "subject_name": cls.subject.subject_name if cls.subject else None,
            "teacher_id": cls.teacher_id,
            "teacher_name": cls.teacher.full_name if cls.teacher else None,
            "semester": cls.semester,
            "year": cls.year,
            "created_at": cls.created_at.isoformat() if cls.created_at else None
        })
    return result

@router.post("/classes")
def create_class(class_data: ClassCreate, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    subject = db.query(Subject).filter(Subject.id == class_data.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    teacher = db.query(Teacher).filter(Teacher.id == class_data.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    last_class = db.query(Class).order_by(Class.id.desc()).first()
    next_number = 1 if not last_class else last_class.id + 1
    class_code = f"LOP{next_number:03d}"

    new_class = Class(
        class_code=class_code,
        class_name=class_data.class_name,
        subject_id=class_data.subject_id,
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

    # Update fields if provided
    if "class_name" in class_data:
        cls.class_name = class_data["class_name"]
    if "teacher_id" in class_data:
        # Verify teacher exists
        teacher = db.query(Teacher).filter(Teacher.id == class_data["teacher_id"]).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        cls.teacher_id = class_data["teacher_id"]
    if "subject_id" in class_data:
        # Verify subject exists
        subject = db.query(Subject).filter(Subject.id == class_data["subject_id"]).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        cls.subject_id = class_data["subject_id"]
    if "semester" in class_data:
        cls.semester = class_data["semester"]
    if "year" in class_data:
        cls.year = class_data["year"]

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

@router.delete("/classes/{class_id}/students/{student_id}")
def remove_student_from_class(class_id: int, student_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    from models import ClassStudent

    enrollment = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == student_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Student not in this class")

    db.delete(enrollment)
    db.commit()
    return {"message": "Student removed from class"}

@router.get("/classes/{class_id}/students")
def get_class_students(class_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    from models import ClassStudent
    import os

    enrollments = db.query(ClassStudent).filter(ClassStudent.class_id == class_id).all()
    students = []
    for enrollment in enrollments:
        student = enrollment.student
        face_data_path = f"../Dataset/FaceData/processed/{student.student_code}"
        has_face_data = os.path.exists(face_data_path) and len(os.listdir(face_data_path)) > 0

        students.append({
            "student_id": student.id,
            "student_code": student.student_code,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "year": student.year,
            "has_face_data": has_face_data
        })

    return students

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

@router.get("/statistics/absence-rate")
def get_absence_rate_statistics(db: Session = Depends(get_db), _admin = Depends(require_admin)):
    from models import AttendanceSession, AttendanceRecord, ClassStudent, Class
    from sqlalchemy import func

    classes = db.query(Class).all()
    statistics = []

    for cls in classes:
        total_sessions = db.query(AttendanceSession).filter(AttendanceSession.class_id == cls.id).count()
        total_students = db.query(ClassStudent).filter(ClassStudent.class_id == cls.id).count()

        if total_sessions == 0 or total_students == 0:
            statistics.append({
                "class_id": cls.id,
                "class_code": cls.class_code,
                "class_name": cls.class_name,
                "total_sessions": total_sessions,
                "total_students": total_students,
                "total_records": 0,
                "present_count": 0,
                "late_count": 0,
                "absent_count": 0,
                "absence_rate": 0.0
            })
            continue

        session_ids = [s.id for s in db.query(AttendanceSession).filter(AttendanceSession.class_id == cls.id).all()]

        total_records = db.query(AttendanceRecord).filter(AttendanceRecord.session_id.in_(session_ids)).count()
        present_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(session_ids),
            AttendanceRecord.status == "present"
        ).count()
        late_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(session_ids),
            AttendanceRecord.status == "late"
        ).count()
        absent_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(session_ids),
            AttendanceRecord.status == "absent"
        ).count()

        expected_records = total_sessions * total_students
        absence_rate = (absent_count / expected_records * 100) if expected_records > 0 else 0.0

        statistics.append({
            "class_id": cls.id,
            "class_code": cls.class_code,
            "class_name": cls.class_name,
            "total_sessions": total_sessions,
            "total_students": total_students,
            "expected_records": expected_records,
            "total_records": total_records,
            "present_count": present_count,
            "late_count": late_count,
            "absent_count": absent_count,
            "absence_rate": round(absence_rate, 2)
        })

    return statistics

@router.get("/statistics/student-absence/{student_id}")
def get_student_absence_statistics(student_id: int, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    from models import AttendanceRecord, AttendanceSession, ClassStudent, Class

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    class_enrollments = db.query(ClassStudent).filter(ClassStudent.student_id == student_id).all()
    class_statistics = []

    for enrollment in class_enrollments:
        cls = enrollment.class_obj
        total_sessions = db.query(AttendanceSession).filter(AttendanceSession.class_id == cls.id).count()

        session_ids = [s.id for s in db.query(AttendanceSession).filter(AttendanceSession.class_id == cls.id).all()]

        total_records = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(session_ids),
            AttendanceRecord.student_id == student_id
        ).count()

        present_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(session_ids),
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.status == "present"
        ).count()

        late_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(session_ids),
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.status == "late"
        ).count()

        absent_count = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id.in_(session_ids),
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.status == "absent"
        ).count()

        absence_rate = (absent_count / total_sessions * 100) if total_sessions > 0 else 0.0

        class_statistics.append({
            "class_id": cls.id,
            "class_code": cls.class_code,
            "class_name": cls.class_name,
            "total_sessions": total_sessions,
            "total_records": total_records,
            "present_count": present_count,
            "late_count": late_count,
            "absent_count": absent_count,
            "absence_rate": round(absence_rate, 2)
        })

    total_sessions_all = sum([stat["total_sessions"] for stat in class_statistics])
    total_absent_all = sum([stat["absent_count"] for stat in class_statistics])
    overall_absence_rate = (total_absent_all / total_sessions_all * 100) if total_sessions_all > 0 else 0.0

    return {
        "student_id": student.id,
        "student_code": student.student_code,
        "full_name": student.full_name,
        "overall_absence_rate": round(overall_absence_rate, 2),
        "class_statistics": class_statistics
    }

# Train model
@router.post("/train-model")
async def train_model(_admin = Depends(require_admin)):
    """Train face recognition model (admin only)"""
    from services.training import training_service
    import asyncio

    loop = asyncio.get_event_loop()
    success, message = await loop.run_in_executor(None, training_service.train_model)

    if success:
        from services.face_recognition import face_recognition_service
        face_recognition_service.model_loaded = False

    return {"success": success, "message": message}

@router.get("/subjects")
def get_all_subjects(db: Session = Depends(get_db), _admin = Depends(require_admin)):
    subjects = db.query(Subject).all()
    return subjects

@router.post("/subjects")
def create_subject(subject_data: SubjectCreate, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    last_subject = db.query(Subject).order_by(Subject.id.desc()).first()
    next_number = 1 if not last_subject else last_subject.id + 1
    subject_code = f"MH{next_number:03d}"

    subject = Subject(
        subject_code=subject_code,
        subject_name=subject_data.subject_name,
        credits=subject_data.credits
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.put("/subjects/{subject_id}")
def update_subject(subject_id: int, subject_data: SubjectCreate, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    subject.subject_name = subject_data.subject_name
    subject.credits = subject_data.credits
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()
    return {"message": "Subject deleted"}

@router.get("/classes/{class_id}/schedules")
def get_class_schedules(class_id: int, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    schedules = db.query(ClassSchedule).filter(ClassSchedule.class_id == class_id).all()
    return schedules

@router.post("/classes/{class_id}/schedules")
def create_class_schedule(class_id: int, schedule_data: ClassScheduleCreate, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    schedule = ClassSchedule(
        class_id=class_id,
        day_of_week=schedule_data.day_of_week,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        room=schedule_data.room,
        mode=schedule_data.mode
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

@router.put("/schedules/{schedule_id}")
def update_schedule(schedule_id: int, schedule_data: ClassScheduleCreate, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    schedule = db.query(ClassSchedule).filter(ClassSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule.day_of_week = schedule_data.day_of_week
    schedule.start_time = schedule_data.start_time
    schedule.end_time = schedule_data.end_time
    schedule.room = schedule_data.room
    schedule.mode = schedule_data.mode
    db.commit()
    db.refresh(schedule)
    return schedule

@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), _admin = Depends(require_admin)):
    schedule = db.query(ClassSchedule).filter(ClassSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted"}
