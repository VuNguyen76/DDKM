import os
from dotenv import load_dotenv
from datetime import time, datetime

load_dotenv()

DB_DIR = os.path.join(os.path.dirname(__file__), "db")
os.makedirs(DB_DIR, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(DB_DIR, 'attendance.db')}")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))

SHIFTS = {
    "Shift1": {
        "name": "Ca 1",
        "start": time(7, 0),
        "end": time(10, 0)
    },
    "Shift2": {
        "name": "Ca 2",
        "start": time(10, 15),
        "end": time(13, 15)
    },
    "Shift3": {
        "name": "Ca 3",
        "start": time(13, 30),
        "end": time(16, 30)
    },
    "Shift4": {
        "name": "Ca 4",
        "start": time(16, 45),
        "end": time(19, 45)
    }
}

def get_current_shift():
    now = datetime.now().time()
    if time(7, 0) <= now < time(10, 15):
        return "Shift1"
    elif time(10, 15) <= now < time(13, 30):
        return "Shift2"
    elif time(13, 30) <= now < time(16, 45):
        return "Shift3"
    elif time(16, 45) <= now < time(20, 0):
        return "Shift4"
    else:
        return None
