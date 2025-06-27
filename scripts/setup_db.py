"""
Python script to create a new "Student Profile" database.
"""
import sqlite3

# Set up a connection the "study_buddy.db" database
conn = sqlite3.connect("study_buddy.db")

# Set up the cursor
cursor = conn.cursor()

# Create a table for Student Profiles
cursor.execute("""
""")

# Create a table for Matching Algorithms
cursor.execute("""
""")

#