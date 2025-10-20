from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import StudentResponse, UserResponse
from models import Student, ClassStudent, AttendanceRecord, FaceData
from routers.auth import require_student, require_teacher, get_current_user_dep
import os
import base64

router = APIRouter(prefix="/api/student", tags=["Student"])

@router.get("/profile", response_model=StudentResponse)
def get_my_profile(db: Session = Depends(get_db), current_user = Depends(require_student)):
    """Get student profile"""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student

@router.get("/classes")
def get_my_classes(db: Session = Depends(get_db), current_user = Depends(require_student)):
    """Get student's classes"""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    class_students = db.query(ClassStudent).filter(ClassStudent.student_id == student.id).all()
    classes = [cs.class_obj for cs in class_students]
    return classes

@router.get("/attendance")
def get_my_attendance(db: Session = Depends(get_db), current_user = Depends(require_student)):
    """Get student's attendance history"""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    records = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student.id).all()
    return records

@router.post("/face-data/{student_id}")
async def upload_face_image(student_id: int, request: dict, db: Session = Depends(get_db), current_user = Depends(require_teacher)):
    """Upload face image for training (teacher/admin only)"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get base64 image from request
    image_base64 = request.get('image_base64')
    if not image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required")

    # Create directory if not exists
    # Remove Vietnamese accents
    import unicodedata
    student_name = student.full_name.lower()
    student_name = unicodedata.normalize('NFD', student_name)
    student_name = ''.join(char for char in student_name if unicodedata.category(char) != 'Mn')
    student_name = student_name.replace(' ', '_')
    upload_dir = f"../Dataset/FaceData/raw/{student_name}"
    os.makedirs(upload_dir, exist_ok=True)

    # Generate filename
    import time
    filename = f"{int(time.time() * 1000)}.jpg"
    file_path = os.path.join(upload_dir, filename)

    # Decode and save image
    try:
        image_data = base64.b64decode(image_base64)
        with open(file_path, "wb") as f:
            f.write(image_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

    # Save to database
    face_data = FaceData(
        student_id=student.id,
        image_path=file_path
    )
    db.add(face_data)
    db.commit()

    return {"message": "Image uploaded successfully", "path": file_path}

@router.get("/face-data")
def get_my_face_data(db: Session = Depends(get_db), current_user = Depends(require_student)):
    """Get student's uploaded face images"""
    face_data = db.query(FaceData).filter(FaceData.user_id == current_user.id).all()
    return face_data

@router.delete("/face-data/{face_id}")
def delete_face_data(face_id: int, db: Session = Depends(get_db), current_user = Depends(require_student)):
    """Delete face image"""
    face_data = db.query(FaceData).filter(
        FaceData.id == face_id,
        FaceData.user_id == current_user.id
    ).first()
    
    if not face_data:
        raise HTTPException(status_code=404, detail="Face data not found")
    
    # Delete file
    if os.path.exists(face_data.image_path):
        os.remove(face_data.image_path)
    
    db.delete(face_data)
    db.commit()
    return {"message": "Face data deleted"}

