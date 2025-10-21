"""
Seed database with sample data
"""
from database import SessionLocal, engine, Base
from models import User, Teacher, Student, Subject, Class, ClassSchedule, ClassStudent
from datetime import time

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data (optional - comment out if you want to keep existing data)
# db.query(ClassStudent).delete()
# db.query(ClassSchedule).delete()
# db.query(Class).delete()
# db.query(Subject).delete()
# db.query(Student).delete()
# db.query(Teacher).delete()
# db.query(User).delete()
# db.commit()

# Create Admin user (skip if exists)
admin_user = db.query(User).filter(User.username == "admin").first()
if not admin_user:
    admin_user = User(username="admin", password="admin", role="admin")
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print("✅ Created admin user")
else:
    print("ℹ️  Admin user already exists")

# Create Teachers (skip if exists)
teachers_data = [
    {"code": "GV001", "name": "Nguyen Thi Anh Updated", "email": "nta.updated@teacher.edu.vn", "phone": "0888888888", "dept": "Math Dept", "password": "newteacher123"},
    {"code": "GV002", "name": "Trần Thị Bình", "email": "ttb@university.edu.vn", "phone": "0901234568", "dept": "Khoa CNTT", "password": "GV002"},
    {"code": "GV003", "name": "Lê Văn Cường", "email": "lvc@university.edu.vn", "phone": "0901234569", "dept": "Khoa CNTT", "password": "GV003"},
]

teachers = []
for t_data in teachers_data:
    # Check if teacher already exists
    existing_teacher = db.query(Teacher).filter(Teacher.teacher_code == t_data["code"]).first()
    if existing_teacher:
        teachers.append(existing_teacher)
        continue

    user = User(username=t_data["code"], password=t_data["password"], role="teacher")
    db.add(user)
    db.commit()
    db.refresh(user)

    teacher = Teacher(
        user_id=user.id,
        teacher_code=t_data["code"],
        full_name=t_data["name"],
        email=t_data["email"],
        phone=t_data["phone"],
        department=t_data["dept"]
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    teachers.append(teacher)
    print(f"✅ Created teacher: {teacher.full_name}")

# Create Students (skip if exists)
students_data = [
    {"code": "SV001", "name": "Pham Van Duc Updated", "email": "pvd.updated@student.edu.vn", "phone": "0999999999", "year": 2024, "password": "newstudent123"},
    {"code": "SV002", "name": "Hoàng Thị Em", "email": "hte@student.edu.vn", "phone": "0912345672", "year": 2024, "password": "SV002"},
    {"code": "SV003", "name": "Vũ Văn Phong", "email": "vvp@student.edu.vn", "phone": "0912345673", "year": 2024, "password": "SV003"},
    {"code": "SV004", "name": "Đặng Thị Giang", "email": "dtg@student.edu.vn", "phone": "0912345674", "year": 2023, "password": "SV004"},
    {"code": "SV005", "name": "Bùi Văn Hùng", "email": "bvh@student.edu.vn", "phone": "0912345675", "year": 2023, "password": "SV005"},
    {"code": "SV006", "name": "Nguyen Van Updated", "email": "updated@example.com", "phone": "0123456789", "year": 2024, "password": "newpassword123"},
]

students = []
for s_data in students_data:
    # Check if student already exists
    existing_student = db.query(Student).filter(Student.student_code == s_data["code"]).first()
    if existing_student:
        students.append(existing_student)
        continue

    user = User(username=s_data["code"], password=s_data["password"], role="student")
    db.add(user)
    db.commit()
    db.refresh(user)

    student = Student(
        user_id=user.id,
        student_code=s_data["code"],
        full_name=s_data["name"],
        email=s_data["email"],
        phone=s_data["phone"],
        year=s_data["year"]
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    students.append(student)
    print(f"✅ Created student: {student.full_name}")

# Create Subjects (skip if exists)
subjects_data = [
    {"code": "MH001", "name": "Toán Cao Cấp 1", "credits": 4},
    {"code": "MH002", "name": "Vật Lý Đại Cương", "credits": 3},
    {"code": "MH003", "name": "Lập Trình C", "credits": 4},
    {"code": "MH004", "name": "Cấu Trúc Dữ Liệu", "credits": 4},
    {"code": "MH005", "name": "Cơ Sở Dữ Liệu", "credits": 3},
    {"code": "MH006", "name": "Lập trình Web", "credits": 3},
    {"code": "MH007", "name": "Lập trình nâng cao", "credits": 4},
]

subjects = []
for subj_data in subjects_data:
    # Check if subject already exists
    existing_subject = db.query(Subject).filter(Subject.subject_code == subj_data["code"]).first()
    if existing_subject:
        subjects.append(existing_subject)
        continue

    subject = Subject(
        subject_code=subj_data["code"],
        subject_name=subj_data["name"],
        credits=subj_data["credits"]
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    subjects.append(subject)
    print(f"✅ Created subject: {subject.subject_name}")

# Create Classes (skip if exists)
classes_data = [
    {"code": "LOP001", "name": "Toán A1", "subject_idx": 0, "teacher_idx": 0, "semester": "2025-1", "year": 2025},
    {"code": "LOP002", "name": "Vật Lý B1", "subject_idx": 1, "teacher_idx": 1, "semester": "2025-1", "year": 2025},
    {"code": "LOP003", "name": "Lập Trình C - LOP003", "subject_idx": 2, "teacher_idx": 2, "semester": "2025-1", "year": 2025},
    {"code": "LOP004", "name": "Lập trình Web - LOP004", "subject_idx": 5, "teacher_idx": 0, "semester": "2025-1", "year": 2025},
    {"code": "LOP005", "name": "Lập trình nâng cao - LOP005", "subject_idx": 6, "teacher_idx": 0, "semester": "2025-1", "year": 2025},
]

classes = []
for c_data in classes_data:
    # Check if class already exists
    existing_class = db.query(Class).filter(Class.class_code == c_data["code"]).first()
    if existing_class:
        classes.append(existing_class)
        continue

    cls = Class(
        class_code=c_data["code"],
        class_name=c_data["name"],
        subject_id=subjects[c_data["subject_idx"]].id,
        teacher_id=teachers[c_data["teacher_idx"]].id,
        semester=c_data["semester"],
        year=c_data["year"]
    )
    db.add(cls)
    db.commit()
    db.refresh(cls)
    classes.append(cls)
    print(f"✅ Created class: {cls.class_name}")

# Create Class Schedules
schedules_data = [
    # LOP001 - Toán A1
    {"class_idx": 0, "day": 2, "start": "07:00:00", "end": "09:00:00", "room": "A101", "mode": "offline"},
    {"class_idx": 0, "day": 4, "start": "13:00:00", "end": "15:00:00", "room": "A101", "mode": "offline"},
    # LOP002 - Vật Lý B1
    {"class_idx": 1, "day": 3, "start": "09:15:00", "end": "11:15:00", "room": "B201", "mode": "offline"},
    # LOP003 - Lập Trình C
    {"class_idx": 2, "day": 5, "start": "07:00:00", "end": "09:00:00", "room": "C301", "mode": "online"},
    # LOP004 - Lập trình Web
    {"class_idx": 3, "day": 2, "start": "07:00:00", "end": "09:00:00", "room": "A101", "mode": "offline"},
    # LOP005 - Lập trình nâng cao
    {"class_idx": 4, "day": 2, "start": "09:15:00", "end": "11:15:00", "room": "A102", "mode": "offline"},
]

for sched_data in schedules_data:
    schedule = ClassSchedule(
        class_id=classes[sched_data["class_idx"]].id,
        day_of_week=sched_data["day"],
        start_time=time.fromisoformat(sched_data["start"]),
        end_time=time.fromisoformat(sched_data["end"]),
        room=sched_data["room"],
        mode=sched_data["mode"]
    )
    db.add(schedule)

db.commit()

# Add students to classes
class_students_data = [
    # LOP001 has students 0,1,2
    {"class_idx": 0, "student_idx": 0},
    {"class_idx": 0, "student_idx": 1},
    {"class_idx": 0, "student_idx": 2},
    # LOP002 has students 2,3,4
    {"class_idx": 1, "student_idx": 2},
    {"class_idx": 1, "student_idx": 3},
    {"class_idx": 1, "student_idx": 4},
    # LOP003 has students 0,3,5
    {"class_idx": 2, "student_idx": 0},
    {"class_idx": 2, "student_idx": 3},
    {"class_idx": 2, "student_idx": 5},
]

for cs_data in class_students_data:
    class_student = ClassStudent(
        class_id=classes[cs_data["class_idx"]].id,
        student_id=students[cs_data["student_idx"]].id
    )
    db.add(class_student)

db.commit()

print("✅ Database seeded successfully!")
print("\n📊 Summary:")
print(f"  - Admin: 1 (username: admin, password: admin)")
print(f"  - Teachers: {len(teachers)}")
print(f"  - Students: {len(students)}")
print(f"  - Subjects: {len(subjects)}")
print(f"  - Classes: {len(classes)}")
print(f"  - Schedules: {len(schedules_data)}")
print(f"  - Class-Student enrollments: {len(class_students_data)}")

print("\n👤 Login credentials:")
print("  Admin: username=admin, password=admin")
print("  Teacher GV001: username=GV001, password=newteacher123")
print("  Student SV001: username=SV001, password=newstudent123")

db.close()

