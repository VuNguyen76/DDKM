from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import User, Student, Class, ClassSchedule, ClassStudent, AttendanceSession, AttendanceRecord, Teacher, Subject
from routers.auth import require_student
from datetime import datetime, date, time
from typing import List
import os
import shutil
from pathlib import Path

router = APIRouter(prefix="/api/student", tags=["student"])

@router.get("/my-schedule")
def get_my_schedule(
    schedule_date: str = None,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    if not user.student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    target_date = datetime.strptime(schedule_date, "%Y-%m-%d").date() if schedule_date else date.today()
    day_of_week = target_date.isoweekday()
    
    enrollments = db.query(ClassStudent).filter(ClassStudent.student_id == user.student.id).all()
    
    schedule_list = []
    for enrollment in enrollments:
        cls = enrollment.class_obj
        schedules = db.query(ClassSchedule).filter(
            ClassSchedule.class_id == cls.id,
            ClassSchedule.day_of_week == day_of_week
        ).all()
        
        for schedule in schedules:
            teacher = db.query(Teacher).filter(Teacher.id == cls.teacher_id).first()
            subject = db.query(Subject).filter(Subject.id == cls.subject_id).first()
            
            schedule_list.append({
                "class_id": cls.id,
                "class_code": cls.class_code,
                "class_name": cls.class_name,
                "subject_code": subject.subject_code if subject else None,
                "subject_name": subject.subject_name if subject else None,
                "teacher_code": teacher.teacher_code if teacher else None,
                "teacher_name": teacher.full_name if teacher else None,
                "start_time": str(schedule.start_time),
                "end_time": str(schedule.end_time),
                "room": schedule.room,
                "mode": schedule.mode,
                "day_of_week": schedule.day_of_week
            })
    
    schedule_list.sort(key=lambda x: x["start_time"])
    
    return {
        "date": str(target_date),
        "day_of_week": day_of_week,
        "schedules": schedule_list
    }

@router.get("/my-classes")
def get_my_classes(
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    if not user.student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    enrollments = db.query(ClassStudent).filter(ClassStudent.student_id == user.student.id).all()
    
    classes = []
    for enrollment in enrollments:
        cls = enrollment.class_obj
        teacher = db.query(Teacher).filter(Teacher.id == cls.teacher_id).first()
        subject = db.query(Subject).filter(Subject.id == cls.subject_id).first()
        
        schedules = db.query(ClassSchedule).filter(ClassSchedule.class_id == cls.id).all()
        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                "day_of_week": schedule.day_of_week,
                "start_time": str(schedule.start_time),
                "end_time": str(schedule.end_time),
                "room": schedule.room,
                "mode": schedule.mode
            })
        
        classes.append({
            "class_id": cls.id,
            "class_code": cls.class_code,
            "class_name": cls.class_name,
            "subject_code": subject.subject_code if subject else None,
            "subject_name": subject.subject_name if subject else None,
            "credits": subject.credits if subject else None,
            "teacher_code": teacher.teacher_code if teacher else None,
            "teacher_name": teacher.full_name if teacher else None,
            "semester": cls.semester,
            "year": cls.year,
            "schedules": schedule_list
        })
    
    return classes

@router.get("/my-attendance")
def get_my_attendance(
    class_id: int = None,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    if not user.student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    if class_id:
        enrollment = db.query(ClassStudent).filter(
            ClassStudent.student_id == user.student.id,
            ClassStudent.class_id == class_id
        ).first()
        if not enrollment:
            raise HTTPException(status_code=404, detail="Not enrolled in this class")
        
        sessions = db.query(AttendanceSession).filter(AttendanceSession.class_id == class_id).all()
    else:
        enrollments = db.query(ClassStudent).filter(ClassStudent.student_id == user.student.id).all()
        class_ids = [e.class_id for e in enrollments]
        sessions = db.query(AttendanceSession).filter(AttendanceSession.class_id.in_(class_ids)).all()
    
    attendance_records = []
    for session in sessions:
        cls = db.query(Class).filter(Class.id == session.class_id).first()
        record = db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session.id,
            AttendanceRecord.student_id == user.student.id
        ).first()
        
        attendance_records.append({
            "session_id": session.id,
            "class_code": cls.class_code,
            "class_name": cls.class_name,
            "session_date": str(session.session_date),
            "start_time": str(session.start_time),
            "end_time": str(session.end_time),
            "status": record.status if record else "absent",
            "check_in_time": str(record.check_in_time) if record and record.check_in_time else None,
            "confidence": record.confidence if record else None
        })
    
    attendance_records.sort(key=lambda x: x["session_date"], reverse=True)
    
    return attendance_records

@router.post("/check-in")
async def student_check_in(
    class_id: int,
    image_base64: str,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    if not user.student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    enrollment = db.query(ClassStudent).filter(
        ClassStudent.student_id == user.student.id,
        ClassStudent.class_id == class_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this class")
    
    today = date.today()
    now = datetime.now()
    current_time = now.time()
    day_of_week = today.isoweekday()
    
    schedule = db.query(ClassSchedule).filter(
        ClassSchedule.class_id == class_id,
        ClassSchedule.day_of_week == day_of_week
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=400, detail="No class scheduled for today")
    
    if current_time < schedule.start_time or current_time > schedule.end_time:
        raise HTTPException(status_code=400, detail=f"Check-in only allowed between {schedule.start_time} and {schedule.end_time}")
    
    session = db.query(AttendanceSession).filter(
        AttendanceSession.class_id == class_id,
        AttendanceSession.session_date == today
    ).first()
    
    if not session:
        session = AttendanceSession(
            class_id=class_id,
            session_date=today,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            created_by=user.id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session.id,
        AttendanceRecord.student_id == user.student.id
    ).first()
    
    if existing_record:
        raise HTTPException(status_code=400, detail="Already checked in for this session")
    
    import base64
    from services.face_recognition import face_recognition_service
    
    try:
        image_data = base64.b64decode(image_base64)
        result = await face_recognition_service.recognize_face(image_data)
        
        if not result or not result.get("student_code"):
            raise HTTPException(status_code=400, detail="Face not recognized")
        
        if result["student_code"] != user.student.student_code:
            raise HTTPException(status_code=400, detail="Face does not match your profile")
        
        status = "present"
        if current_time > schedule.start_time:
            time_diff = (datetime.combine(today, current_time) - datetime.combine(today, schedule.start_time)).total_seconds() / 60
            if time_diff > 15:
                status = "late"
        
        record = AttendanceRecord(
            session_id=session.id,
            student_id=user.student.id,
            status=status,
            check_in_time=now,
            confidence=result.get("confidence")
        )
        db.add(record)
        db.commit()
        
        return {
            "success": True,
            "status": status,
            "check_in_time": str(now),
            "confidence": result.get("confidence"),
            "message": f"Checked in successfully as {status}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check-in failed: {str(e)}")


@router.post("/upload-face-images")
async def upload_face_images(
    files: List[UploadFile] = File(...),
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Upload face images for training"""
    if not user.student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    student_code = user.student.student_code

    # Create directory for student's face data
    base_dir = Path("Dataset/FaceData/processed")
    student_dir = base_dir / student_code
    student_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []
    for file in files:
        if not file.content_type.startswith("image/"):
            continue

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        ext = os.path.splitext(file.filename)[1]
        filename = f"{student_code}_{timestamp}{ext}"
        file_path = student_dir / filename

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append({
            "filename": filename,
            "path": str(file_path)
        })

    return {
        "success": True,
        "uploaded_count": len(uploaded_files),
        "files": uploaded_files,
        "message": f"Uploaded {len(uploaded_files)} images for {student_code}"
    }


@router.get("/my-face-images")
def get_my_face_images(
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Get list of uploaded face images"""
    if not user.student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    student_code = user.student.student_code
    student_dir = Path("Dataset/FaceData/processed") / student_code

    if not student_dir.exists():
        return {"images": [], "count": 0}

    images = []
    for img_file in student_dir.glob("*"):
        if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            images.append({
                "filename": img_file.name,
                "size": img_file.stat().st_size,
                "created_at": datetime.fromtimestamp(img_file.stat().st_ctime).isoformat()
            })

    return {
        "images": images,
        "count": len(images),
        "student_code": student_code
    }


@router.delete("/my-face-images/{filename}")
def delete_my_face_image(
    filename: str,
    user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Delete a face image"""
    if not user.student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    student_code = user.student.student_code
    file_path = Path("Dataset/FaceData/processed") / student_code / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    # Security check: ensure filename doesn't contain path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path.unlink()

    return {
        "success": True,
        "message": f"Deleted {filename}"
    }
