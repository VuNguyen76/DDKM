import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db/attendance.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE class_schedules ADD COLUMN mode VARCHAR(20) DEFAULT 'offline'"))
        conn.commit()
        print("✅ Added 'mode' column to class_schedules table")
    except Exception as e:
        print(f"Column might already exist or error: {e}")

