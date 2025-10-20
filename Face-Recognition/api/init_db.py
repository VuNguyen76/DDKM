from database import SessionLocal, engine, Base
from models import Teacher, Class

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

teacher = Teacher(
    teacher_code="T001",
    full_name="Giáo viên mặc định",
    email="teacher@example.com",
    phone="0123456789",
    department="Khoa CNTT"
)
db.add(teacher)
db.commit()
db.refresh(teacher)

default_class = Class(
    class_code="CS101",
    class_name="Lớp Khoa học máy tính 101",
    teacher_id=teacher.id,
    semester="2025-1",
    year=2025
)
db.add(default_class)
db.commit()

print("Database initialized successfully!")
print(f"Admin login: username=admin, password=admin")
print(f"Created teacher: {teacher.full_name} (Code: {teacher.teacher_code})")
print(f"Created class: {default_class.class_name} (Code: {default_class.class_code})")

db.close()
