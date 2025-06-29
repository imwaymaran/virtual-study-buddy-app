import sqlite3
import os

from config import DB_PATH

def get_or_create_subject(cursor, subject_name):
    """
    Retrieve subject_id for a given subject name, inserting it if not found.
    
    Args:
        cursor: SQLite cursor object.
        subject_name (str): Name of the subject to lookup or insert.
    
    Returns:
        int: subject_id from the database.
    """
    cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = ?", (subject_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO subjects (subject_name) VALUES (?)", (subject_name,))
    return cursor.lastrowid

def get_next_student_id():
    """
    Generate the next available student ID based on the existing IDs in the database.

    Assumes that student IDs are stored as strings with the format 'stu####',
    where #### is a numeric value (e.g., 'stu1000', 'stu1001', etc.).

    Returns:
        str: The next student ID in the sequence (e.g., 'stu1155' if 'stu1154' is the highest).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM students")
        ids = [int(row[0][3:]) for row in cursor.fetchall()]
        max_id = max(ids)
        return f"stu{max_id + 1}"