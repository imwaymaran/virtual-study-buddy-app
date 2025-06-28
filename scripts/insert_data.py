"""
Python script to populate the Virtual Study Buddy SQLite database with mock student data.

This script loads student data from a CSV file and inserts it into the database. It populates:
- students: includes UTC-adjusted study start and end times
- study_days: local weekday availability per student
- utc_study_days: converted weekday availability in UTC
- subjects: list of subjects (created dynamically from student preferences)
- student_subjects: links each student to their preferred subjects (many-to-many)

Timezone conversions and study time ranges are handled automatically using utility functions.

Note:
- This script assumes the database schema has already been created (e.g., by running setup_db.py).
- Run this script after setup_db.py to populate the database with initial data.
- You can re-run it to refresh or overwrite the dataset.

To execute, run this file directly. The logic is contained within the main() function.
"""

import os
import sqlite3
from datetime import datetime, timedelta
import pandas as pd

from utils.time_utils import STUDY_TIME_RANGES, parse_utc_offset, shift_to_utc, get_utc_day
from utils.db_utils import get_or_create_subject

def main():
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, '..', 'data', 'raw', 'students.csv')
    db_path = os.path.join(base_dir, '..', 'data', 'processed', 'study_buddy.db')

    df = pd.read_csv(csv_path)
    
    success_count = 0

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():
            utc_offset = parse_utc_offset(row['timezone'])
            local_start, local_end = STUDY_TIME_RANGES.get(row['study_times'], ('00:00', '00:00'))
            utc_start_time = shift_to_utc(local_start, utc_offset)
            utc_end_time = shift_to_utc(local_end, utc_offset)

            cursor.execute('''
                INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['student_id'],
                row['student_name'],
                row['personality_type'],
                row['study_style'],
                utc_offset,
                row['experience_level'],
                row['GPA'],
                utc_start_time,
                utc_end_time
            ))
            
            if cursor.rowcount > 0:
                success_count += 1

            days = [d.strip() for d in row['days_of_wk_avail'].split(',')]
            for day in days:
                cursor.execute(
                    'INSERT OR IGNORE INTO study_days (student_id, day) VALUES (?, ?)',
                    (row['student_id'], day)
                )
                utc_day = get_utc_day(day, local_start, utc_offset)
                cursor.execute(
                    'INSERT OR IGNORE INTO utc_study_days (student_id, utc_day) VALUES (?, ?)',
                    (row['student_id'], utc_day)
                )

            subjects = [s.strip() for s in row['preferred_subjects'].split(',')]
            for subject_name in subjects:
                subject_id = get_or_create_subject(cursor, subject_name)
                cursor.execute(
                    "INSERT OR IGNORE INTO student_subjects (student_id, subject_id) VALUES (?, ?)",
                    (row['student_id'], subject_id)
                )
                
    print(f"{success_count} students successfully inserted or replaced in the database.")


if __name__ == "__main__":
    main()