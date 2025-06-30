"""
Python script to initialize the SQLite database for the Virtual Study Buddy App.

This script sets up the core database schema, including the following tables:
- students: stores student profile info including timezone-adjusted study availability
- subjects: list of supported study subjects
- student_subjects: maps students to their preferred subjects (many-to-many)
- study_days: stores students’ preferred study days (local time)
- utc_study_days: stores preferred study days converted to UTC for global matching

Optional tables like messages and notifications are defined in the code but commented out
until needed.

Note: This script only sets up the database schema. Data import from the CSV file and any
matching or messaging logic should be handled in separate scripts.

Run this script once to initialize the database structure. Re-run only if schema changes are made.
"""

import sqlite3
import os

def initialize_database():
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, '..', 'data', 'processed', 'study_buddy.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        student_name TEXT NOT NULL, 
        personality_type TEXT,
        study_style TEXT NOT NULL,
        utc_offset INTEGER NOT NULL,
        experience_level TEXT NOT NULL,
        GPA REAL,
        utc_start_time TEXT NOT NULL,   
        utc_end_time TEXT NOT NULL     
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_subjects (
        student_id TEXT,
        subject_id INTEGER,
        PRIMARY KEY (student_id, subject_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_days (
        student_id TEXT,
        day TEXT CHECK (day IN ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')),
        PRIMARY KEY (student_id, day),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS utc_study_days (
        student_id TEXT,
        utc_day TEXT CHECK (utc_day IN ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')),
        PRIMARY KEY (student_id, utc_day),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    # NOTE: Messaging and notification features are defined below but
    #       disabled for the MVP. Uncomment them when ready to use.
    # # Messages table 
    # cursor.execute('''
    # CREATE TABLE IF NOT EXISTS messages (
    #     message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     sender_id TEXT,
    #     receiver_id TEXT,
    #     content TEXT,
    #     timestamp TEXT,
    #     FOREIGN KEY(sender_id) REFERENCES students(student_id),
    #     FOREIGN KEY(receiver_id) REFERENCES students(student_id)
    # )
    # ''')
    
    # Scheduled study sessions
    # cursor.execute("""
    # CREATE TABLE IF NOT EXISTS scheduled_sessions (
    #     session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     host_student_id TEXT NOT NULL,
    #     guest_student_id TEXT,
    #     day TEXT NOT NULL,
    #     start_time TEXT NOT NULL,
    #     end_time TEXT NOT NULL,
    #     status TEXT DEFAULT 'pending',
    #     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    #     FOREIGN KEY (host_student_id) REFERENCES students(student_id),
    #     FOREIGN KEY (guest_student_id) REFERENCES students(student_id)
    # );
    # """)
    
    # Notifications table (optional feature)
    # cursor.execute('''
    # CREATE TABLE IF NOT EXISTS notifications (
    #      notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #      student_id TEXT,
    #      type TEXT,
    #      content TEXT,
    #      status TEXT,
    #      timestamp TEXT,
    #      FOREIGN KEY(student_id) REFERENCES students(student_id)
    #  )
    #  ''')

    conn.commit()
    conn.close()
# Run this when needed
if __name__ == "__main__":
    initialize_database()