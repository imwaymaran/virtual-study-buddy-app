"""
Python script to create the Virtual Study Buddy database from a mock CSV file.

This script sets up the SQLite database for the Virtual Study Buddy App.
It creates the necessary tables:
- students: stores student profile information
- subjects: maps students to their preferred subjects
- availability: tracks each student’s weekly availability
- messages: stores chat messages between students
- notifications: stores reminders or nudges for app activity

It also loads initial mock data from the CSV file and inserts it into the appropriate tables.

Note: This script should be run once to initialize the database. If changes are made to the schema, 
you may need to delete the existing database and rerun this script.

"""

# Import Libraries
import sqlite3
import pandas as pd
import os 

# Load CSV Files
df = pd.read_csv("data/Virtual Study Buddy_ Mock Data Set - virtual_study_buddy_mock_data.csv")

# Connect to the database
conn = sqlite3.connect("db/study_buddy.db")
cursor = conn.cursor()

# Create a table for Student Profiles
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    student_name TEXT NOT NULL, -- NOT NULL ensure that there are no empty values
    study_times TEXT NOT NULL,
    personality_type TEXT,
    study_style TEXT NOT NULL,
    timezone TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    GPA REAL                    -- REAL allows for decimal values
)
""")

# Create a table for Subjects
cursor.execute('''
CREATE TABLE IF NOT EXISTS subjects (
    student_id TEXT,
    subject TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)
''')

# Availability table
cursor.execute('''
CREATE TABLE IF NOT EXISTS availability (
    student_id TEXT,
    day_of_week TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)
''')

# Messages table 
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id TEXT,
    receiver_id TEXT,
    content TEXT,
    timestamp TEXT,
    FOREIGN KEY(sender_id) REFERENCES students(student_id),
    FOREIGN KEY(receiver_id) REFERENCES students(student_id)
)
''')

# Notifications table (optional feature)
cursor.execute('''
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    type TEXT,
    content TEXT,
    status TEXT,
    timestamp TEXT,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)
''')

# Insert Data into Students Table
for i, row in df.iterrows():
    cursor.execute('''
    INSERT OR REPLACE INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['student_id'],
        row['student_name'],
        row['study_times'],
        row['personality_type'],
        row['study_style'],
        row['timezone'],
        row['experience_level'],
        row['GPA']
    ))

# Insert data into Subjects Table 
for i, row in df.iterrows():
    subjects = [s.strip() for s in row['preferred_subjects'].split(',')]
    for subject in subjects:
        cursor.execute('''
            INSERT INTO subjects (student_id, subject) VALUES (?, ?)
        ''', (row['student_id'], subject))

# Insert data into Availability Table
for i, row in df.iterrows():
    days = [d.strip() for d in row['days_of_wk_avail'].split(',')]
    for day in days:
        cursor.execute('''
            INSERT INTO availability (student_id, day_of_week) VALUES (?, ?)
        ''', (row['student_id'], day))

# Save and close the connection
conn.commit()
conn.close()