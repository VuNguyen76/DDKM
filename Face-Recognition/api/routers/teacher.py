from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import ClassCreate, ClassResponse, AttendanceSessionCreate, AttendanceSessionResponse, AttendanceSummary, AttendanceRecordResponse
from models import Class, Teacher, AttendanceSession, AttendanceRecord, ClassStudent, Student, AttendanceStatus
from routers.auth import require_teacher, get_current_user_dep

router = APIRouter(prefix="/api/teacher", tags=["Teacher"])

# Class management
@router.get("/classes", response_model=List[ClassResponse])
def get_my_classes(db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Get teacher's classes (admin can see all classes)"""
    # Admin can see all classes
    if current_user.role.value == "admin":
        classes = db.query(Class).all()
        return classes

    # Teacher can only see their classes
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail=f"Teacher profile not found for user_id={current_user.id}")

    classes = db.query(Class).filter(Class.teacher_id == teacher.id).all()
    return classes

@router.post("/classes", response_model=ClassResponse)
def create_class(class_data: ClassCreate, db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Create new class"""
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    new_class = Class(
        class_code=class_data.class_code,
        class_name=class_data.class_name,
        teacher_id=teacher.id,
        semester=class_data.semester,
        year=class_data.year,
        schedule=class_data.schedule
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

@router.get("/classes/{class_id}/students")
def get_class_students(class_id: int, db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Get students in class"""
    class_students = db.query(ClassStudent).filter(ClassStudent.class_id == class_id).all()
    students = [cs.student for cs in class_students]
    return students

@router.post("/classes/{class_id}/students")
def add_student_to_class(class_id: int, student_id: int, db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Add student to class"""
    # Check if already enrolled
    existing = db.query(ClassStudent).filter(
        ClassStudent.class_id == class_id,
        ClassStudent.student_id == student_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled")
    
    class_student = ClassStudent(class_id=class_id, student_id=student_id)
    db.add(class_student)
    db.commit()
    return {"message": "Student added to class"}

# Attendance session management
@router.post("/attendance/sessions", response_model=AttendanceSessionResponse)
def create_attendance_session(session_data: AttendanceSessionCreate, db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Create attendance session (admin and teacher)"""
    # Admin can create session for any class
    if current_user.role.value == "admin":
        # Use first teacher as creator (or create a default teacher)
        teacher = db.query(Teacher).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="No teacher found in system")
    else:
        # Teacher can only create session for their classes
        teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher profile not found")

    session = AttendanceSession(
        class_id=session_data.class_id,
        session_name=session_data.session_name,
        session_date=session_data.session_date,
        created_by=teacher.id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/attendance/sessions", response_model=List[AttendanceSessionResponse])
def get_my_sessions(db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Get attendance sessions (admin can see all)"""
    # Admin can see all sessions
    if current_user.role.value == "admin":
        sessions = db.query(AttendanceSession).all()
        return sessions

    # Teacher can only see their sessions
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    sessions = db.query(AttendanceSession).filter(AttendanceSession.created_by == teacher.id).all()
    return sessions

@router.get("/attendance/sessions/{session_id}", response_model=AttendanceSessionResponse)
def get_session_detail(session_id: int, db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Get attendance session detail"""
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/attendance/sessions/{session_id}/summary", response_model=AttendanceSummary)
def get_session_summary(session_id: int, db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Get attendance summary - simple count and list"""
    session = db.query(AttendanceSession).filter(AttendanceSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get all students in class
    class_students = db.query(ClassStudent).filter(ClassStudent.class_id == session.class_id).all()
    all_students = [cs.student for cs in class_students]
    
    # Get attendance records
    records = db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()
    
    # Categorize students
    present_students = []
    late_students = []
    absent_student_ids = set(s.id for s in all_students)
    
    for record in records:
        if record.status == AttendanceStatus.PRESENT:
            present_students.append(record.student)
            absent_student_ids.discard(record.student_id)
        elif record.status == AttendanceStatus.LATE:
            late_students.append(record.student)
            absent_student_ids.discard(record.student_id)
    
    absent_students = [s for s in all_students if s.id in absent_student_ids]
    
    return {
        "total_students": len(all_students),
        "present_count": len(present_students),
        "absent_count": len(absent_students),
        "late_count": len(late_students),
        "present_students": present_students,
        "absent_students": absent_students,
        "late_students": late_students
    }

@router.put("/attendance/records/{record_id}")
def update_attendance_record(record_id: int, status: AttendanceStatus, db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Update attendance record"""
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    record.status = status
    db.commit()
    return {"message": "Record updated"}

