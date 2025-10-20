import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(__file__))
load_dotenv()

from database import Base, get_db
from models import User, Student, Teacher, Subject, Class, ClassSchedule, ClassStudent, AttendanceSession, AttendanceRecord, Session, ADMIN_USERNAME, ADMIN_PASSWORD

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db/attendance.db")

def migrate_database():
    print("=" * 60)
    print("DATABASE MIGRATION TO NEW SCHEMA")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("\n[1/8] Dropping old tables...")
        Base.metadata.drop_all(bind=engine)
        print("✓ Old tables dropped")
        
        print("\n[2/8] Creating new tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ New tables created")
        
        print("\n[3/8] Creating admin user...")
        admin_user = User(
            username=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            role="admin",
            student_id=None
        )
        db.add(admin_user)
        db.commit()
        print(f"✓ Admin user created: {ADMIN_USERNAME}/{ADMIN_PASSWORD}")
        
        print("\n[4/8] Creating sample subjects...")
        subjects_data = [
            {"subject_name": "Toán Cao Cấp 1", "credits": 4, "description": "Giải tích và đại số tuyến tính"},
            {"subject_name": "Lập Trình Python", "credits": 3, "description": "Lập trình cơ bản với Python"},
            {"subject_name": "Cơ Sở Dữ Liệu", "credits": 3, "description": "Thiết kế và quản lý CSDL"},
            {"subject_name": "Mạng Máy Tính", "credits": 3, "description": "Kiến trúc và giao thức mạng"},
            {"subject_name": "Trí Tuệ Nhân Tạo", "credits": 4, "description": "Machine Learning và Deep Learning"},
        ]
        
        subjects = []
        for idx, data in enumerate(subjects_data, 1):
            subject = Subject(
                subject_code=f"MH{idx:03d}",
                subject_name=data["subject_name"],
                credits=data["credits"],
                description=data["description"]
            )
            db.add(subject)
            subjects.append(subject)
        
        db.commit()
        print(f"✓ Created {len(subjects)} subjects")
        for s in subjects:
            print(f"  - {s.subject_code}: {s.subject_name} ({s.credits} tín chỉ)")
        
        print("\n[5/8] Creating sample teachers...")
        teachers_data = [
            {"full_name": "Nguyễn Văn An", "email": "nva@university.edu.vn", "phone": "0901234567", "department": "Khoa Toán"},
            {"full_name": "Trần Thị Bình", "email": "ttb@university.edu.vn", "phone": "0901234568", "department": "Khoa CNTT"},
            {"full_name": "Lê Văn Cường", "email": "lvc@university.edu.vn", "phone": "0901234569", "department": "Khoa CNTT"},
        ]

        teachers = []
        for idx, data in enumerate(teachers_data, 1):
            teacher_code = f"GV{idx:03d}"
            teacher = Teacher(
                teacher_code=teacher_code,
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                department=data["department"],
                password=teacher_code
            )
            db.add(teacher)
            teachers.append(teacher)

        db.commit()

        for teacher in teachers:
            user = User(
                username=teacher.teacher_code,
                password=teacher.password,
                role="teacher",
                teacher_id=teacher.id
            )
            db.add(user)

        db.commit()
        print(f"✓ Created {len(teachers)} teachers with user accounts")
        for t in teachers:
            print(f"  - {t.teacher_code}: {t.full_name} - {t.department} (password: {t.password})")
        
        print("\n[6/8] Creating sample students...")
        students_data = [
            {"full_name": "Phạm Văn Đức", "email": "pvd@student.edu.vn", "phone": "0912345671", "year": 2024},
            {"full_name": "Hoàng Thị Em", "email": "hte@student.edu.vn", "phone": "0912345672", "year": 2024},
            {"full_name": "Vũ Văn Phong", "email": "vvp@student.edu.vn", "phone": "0912345673", "year": 2024},
            {"full_name": "Đặng Thị Giang", "email": "dtg@student.edu.vn", "phone": "0912345674", "year": 2023},
            {"full_name": "Bùi Văn Hùng", "email": "bvh@student.edu.vn", "phone": "0912345675", "year": 2023},
        ]
        
        students = []
        for idx, data in enumerate(students_data, 1):
            student_code = f"SV{idx:03d}"
            student = Student(
                student_code=student_code,
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                year=data["year"],
                password=student_code
            )
            db.add(student)
            students.append(student)
        
        db.commit()
        
        for student in students:
            user = User(
                username=student.student_code,
                password=student.password,
                role="student",
                student_id=student.id
            )
            db.add(user)
        
        db.commit()
        print(f"✓ Created {len(students)} students with user accounts")
        for s in students:
            print(f"  - {s.student_code}: {s.full_name} (password: {s.password})")
        
        print("\n[7/8] Creating sample classes with schedules...")
        classes_data = [
            {
                "class_name": "Toán A1",
                "subject_id": subjects[0].id,
                "teacher_id": teachers[0].id,
                "semester": "HK1",
                "year": 2024,
                "schedules": [
                    {"day_of_week": 2, "start_time": "07:00", "end_time": "09:00", "room": "A101"},
                    {"day_of_week": 4, "start_time": "13:00", "end_time": "15:00", "room": "A101"},
                ]
            },
            {
                "class_name": "Python B1",
                "subject_id": subjects[1].id,
                "teacher_id": teachers[1].id,
                "semester": "HK1",
                "year": 2024,
                "schedules": [
                    {"day_of_week": 3, "start_time": "07:00", "end_time": "09:00", "room": "B201"},
                    {"day_of_week": 5, "start_time": "09:15", "end_time": "11:15", "room": "B201"},
                ]
            },
            {
                "class_name": "CSDL C1",
                "subject_id": subjects[2].id,
                "teacher_id": teachers[2].id,
                "semester": "HK1",
                "year": 2024,
                "schedules": [
                    {"day_of_week": 2, "start_time": "13:00", "end_time": "15:00", "room": "C301"},
                ]
            },
        ]
        
        classes = []
        for idx, data in enumerate(classes_data, 1):
            class_obj = Class(
                class_code=f"LOP{idx:03d}",
                class_name=data["class_name"],
                subject_id=data["subject_id"],
                teacher_id=data["teacher_id"],
                semester=data["semester"],
                year=data["year"]
            )
            db.add(class_obj)
            db.commit()
            db.refresh(class_obj)
            
            for schedule_data in data["schedules"]:
                from datetime import time
                start_parts = schedule_data["start_time"].split(":")
                end_parts = schedule_data["end_time"].split(":")
                
                schedule = ClassSchedule(
                    class_id=class_obj.id,
                    day_of_week=schedule_data["day_of_week"],
                    start_time=time(int(start_parts[0]), int(start_parts[1])),
                    end_time=time(int(end_parts[0]), int(end_parts[1])),
                    room=schedule_data["room"]
                )
                db.add(schedule)
            
            classes.append(class_obj)
        
        db.commit()
        print(f"✓ Created {len(classes)} classes with schedules")
        for c in classes:
            print(f"  - {c.class_code}: {c.class_name}")
            schedules = db.query(ClassSchedule).filter(ClassSchedule.class_id == c.id).all()
            for sch in schedules:
                days = {2: "Thứ 2", 3: "Thứ 3", 4: "Thứ 4", 5: "Thứ 5", 6: "Thứ 6", 7: "Chủ nhật"}
                print(f"    {days[sch.day_of_week]}, {sch.start_time}-{sch.end_time}, Phòng {sch.room}")
        
        print("\n[8/8] Enrolling students to classes...")
        enrollments = [
            (classes[0].id, [students[0].id, students[1].id, students[2].id]),
            (classes[1].id, [students[0].id, students[3].id, students[4].id]),
            (classes[2].id, [students[1].id, students[2].id, students[3].id]),
        ]
        
        total_enrollments = 0
        for class_id, student_ids in enrollments:
            for student_id in student_ids:
                enrollment = ClassStudent(
                    class_id=class_id,
                    student_id=student_id
                )
                db.add(enrollment)
                total_enrollments += 1
        
        db.commit()
        print(f"✓ Created {total_enrollments} student enrollments")
        
        for class_obj in classes:
            enrollments = db.query(ClassStudent).filter(ClassStudent.class_id == class_obj.id).all()
            print(f"  - {class_obj.class_code}: {len(enrollments)} students")
            for enr in enrollments:
                student = db.query(Student).filter(Student.id == enr.student_id).first()
                print(f"    • {student.student_code}: {student.full_name}")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📊 SUMMARY:")
        print(f"  - Users: {db.query(User).count()} (1 admin + {len(teachers)} teachers + {len(students)} students)")
        print(f"  - Subjects: {db.query(Subject).count()}")
        print(f"  - Teachers: {db.query(Teacher).count()}")
        print(f"  - Students: {db.query(Student).count()}")
        print(f"  - Classes: {db.query(Class).count()}")
        print(f"  - Class Schedules: {db.query(ClassSchedule).count()}")
        print(f"  - Student Enrollments: {db.query(ClassStudent).count()}")

        print("\n🔑 LOGIN CREDENTIALS:")
        print(f"  Admin: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
        print(f"  Teachers: GV001-GV{len(teachers):03d} / (password = teacher_code)")
        print(f"  Students: SV001-SV{len(students):03d} / (password = student_code)")

        print("\n✅ Database is ready to use!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database()

