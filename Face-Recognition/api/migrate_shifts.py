from database import SessionLocal
from models import AttendanceSession
from datetime import time

OLD_TO_NEW_SHIFT = {
    "Morning": "Shift1",
    "Afternoon": "Shift3",
    "Evening": "Shift4"
}

SHIFT_TIMES = {
    "Shift1": {"start": time(7, 0), "end": time(10, 0)},
    "Shift2": {"start": time(10, 15), "end": time(13, 15)},
    "Shift3": {"start": time(13, 30), "end": time(16, 30)},
    "Shift4": {"start": time(16, 45), "end": time(19, 45)}
}

def migrate_shifts():
    db = SessionLocal()
    try:
        sessions = db.query(AttendanceSession).all()
        print(f"Found {len(sessions)} sessions to migrate")
        
        for session in sessions:
            if hasattr(session, 'shift') and session.shift in OLD_TO_NEW_SHIFT:
                old_shift = session.shift
                new_shift = OLD_TO_NEW_SHIFT[old_shift]
                session.shift = new_shift
                
                if new_shift in SHIFT_TIMES:
                    session.start_time = SHIFT_TIMES[new_shift]["start"]
                    session.end_time = SHIFT_TIMES[new_shift]["end"]
                
                print(f"Migrated session {session.id}: {old_shift} -> {new_shift}")
        
        db.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_shifts()

