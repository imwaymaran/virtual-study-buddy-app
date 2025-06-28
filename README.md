# Virtual Study Buddy App

## Project Overview

The Virtual Study Buddy App is a matching tool designed to connect students based on study habits, availability, and learning goals. It organizes student profiles and preferences in a structured database, enabling simulation of intelligent pairing using Python and SQL.

---

## Database Schema Overview

The raw data was generated via Mockaroo and saved as virtual_study_buddy_mock_data.csv. The data fields are as follows: student_id, student_name, preferred_subjects, study_times, study_style, personality_type, timezone, experience_level, GPA.

This database supports the core functionality of the Virtual Study Buddy App. It organizes student profiles, subjects of interest, and weekly availability to enable effective matching based on study preferences and schedules. The tables for messaging and notifications allow for organizing the data structure for real-time communication and personalized nudges. The structure is built to keep things organized and support additional features as the app grows.

### Tables

| Table Name         | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `students`         | Stores individual student profiles including UTC-adjusted study hours      |
| `subjects`         | Unique list of all study subjects                                          |
| `student_subjects` | Many-to-many mapping between students and their preferred subjects         |
| `study_days`       | Stores students’ availability by local weekdays                            |
| `utc_study_days`   | Stores availability adjusted to UTC weekdays for easier time zone matching  |
| `messages`         | (Optional) Stores chat messages between students                           |
| `notifications`    | (Optional) Stores reminders and alerts                                     |

---

### `students`

| Column           | Type  | Description                                  |
|------------------|-------|----------------------------------------------|
| student_id       | TEXT  | Unique student identifier (Primary Key)      |
| student_name     | TEXT  | Full name                                    |
| personality_type | TEXT  | MBTI type                                    |
| study_style      | TEXT  | Pair / Group / Flexible                      |
| timezone         | INT   | UTC offset in hours                          |
| experience_level | TEXT  | Beginner / Intermediate / Advanced           |
| GPA              | REAL  | Grade Point Average                          |
| utc_start_time   | TEXT  | Study start time in UTC                      |
| utc_end_time     | TEXT  | Study end time in UTC                        |

### `subjects`

| Column        | Type | Description                   |
|---------------|------|-------------------------------|
| subject_id    | INT  | Primary Key                   |
| subject_name  | TEXT | Unique subject name           |

### `student_subjects`

| Column       | Type | Description                         |
|--------------|------|-------------------------------------|
| student_id   | TEXT | Foreign key to `students` table     |
| subject_id   | INT  | Foreign key to `subjects` table     |

### `study_days`

| Column       | Type | Description                         |
|--------------|------|-------------------------------------|
| student_id   | TEXT | Foreign key to `students` table     |
| day          | TEXT | Local weekday abbreviation (e.g., Mon) |

### `utc_study_days`

| Column       | Type | Description                         |
|--------------|------|-------------------------------------|
| student_id   | TEXT | Foreign key to `students` table     |
| utc_day      | TEXT | UTC weekday abbreviation            |

---

## Tools & Libraries

- Python
- SQLite
- pandas
- datetime

---

## Python Scripts

- `setup_db.py`: Initializes the SQLite schema (tables, relationships)
- `insert_data.py`: Loads mock CSV data, handles UTC conversion, and populates the database
- `query_db.py`: (Planned) Implements basic matching logic between students

---

## Matching Logic

**Goal:** Simulate Pairing

**Criteria:**

- Shared subjects
- Overlapping availability
- (Optional) Similar study style or compatible personality type

**Approach:**

- Read from SQLite into pandas
- Join/merge tables
- Group & filter based on overlap rules
- Output: List of ideal matches per student

---

## Folder Structure

```plaintext
virtual-study-buddy-app/
├── data/
│   ├── raw/
│   │   └── students.csv               # Mockaroo-generated raw dataset
│   └── processed/
│       └── study_buddy.db             # Final SQLite database
├── scripts/
│   ├── insert_data.py                 # Populates the database from CSV
│   ├── setup_db.py                    # Initializes the database schema
│   ├── utils/
│   │   ├── time_utils.py              # Handles time conversion and UTC logic
│   │   └── db_utils.py                # Database helper functions
├── notebooks/
│   └── analysis.ipynb                 # Optional: for exploratory queries
└── README.md                          # Project overview and instructions
```

# User App Flow 

---

## Contributors

**Data Science Fellows**
- Adewale Thompson
- Akisha Robinson
- Gennadii Ershov
- Jasmin Sweat
- Zahrea Franklin
- Zakiyyah Jones
- Julissa Morales

**Bloomberg Mentors**
- Karishma Borole
- Yogesh Bhatti

---

## License

This project was developed solely for educational and demonstration purposes during a hackathon. We do not claim ownership of the data used; it was generated via [Mockaroo](https://mockaroo.com) and used strictly to simulate a study buddy matching system.  
No real user information is stored, collected, or shared.
