# virtual-study-buddy-app

# Project Overview
The Virtual Study Buddy App is a matching tool designed to connect students based on their study habits, availability, and learning goals. By organizing student profiles and preferences in a structured dataset, we can simulate  matching using Python and SQL. 

# Database Schema Overview
The raw data was generated via Mockaroo and saved as virtual_study_buddy_mock_data.csv. The data fields are as follows: student_id, student_name, preferred_subjects, study_times, study_style, personality_type, timezone, experience_level, GPA.

This database supports the core functionality of the Virtual Study Buddy App. It organizes student profiles, subjects of interest, and weekly availability to enable effective matching based on study preferences and schedules. The tables for messaging and notifications allow for organizing the data structure for real-time communication and personalized nudges. The structure is built to keep things organized and support additional features as the app grows.

## General Overview
| Table Name    | Description                                                |
|---------------|------------------------------------------------------------|
| Students      | Stores individual student profiles                         |
| Subjects      | Tracks each student to the subjects they are studying      |
| Availability  | Tracks each student’s weekly availability                  |
| Messages      | Stores chat messages exchanged between students            |
| Notifications | Stores alerts like daily check-ins or chat reminders       |


### Students
| Column           | Type  | Description                                  |
|------------------|-------|----------------------------------------------|
| student_id       | TEXT  | Primary key, uniquely identifies a student   |
| student_name     | TEXT  | Full name of the student                     |
| personality_type | TEXT  | MBTI type                                    |
| study_style      | TEXT  | Pair/Group/Flexible (Group Formation)        |
| timezone         | TEXT  | Student’s time zone (EST, PST)               |
| experience_level | TEXT  | Beginner, Intermediate, Advanced             |
| GPA              | REAL  | Grade Point Average (can be decimal)         |


### Subjects 
| Column            | Type | Description                                  |
|-------------------|------|----------------------------------------------|
| student_id        | TEXT | Foreign key referencing students table       |
| preferred_subject | TEXT | Subject associated with the student          |


### Availability
| Column        | Type | Description                                  |
|---------------|------|----------------------------------------------|
| student_id    | TEXT | Foreign key referencing students table       |
| days_of_week  | TEXT | Week day the student is available            |


### Chat
| Column      | Type     | Description                                  |
|-------------|----------|----------------------------------------------|
| message_id  | INTEGER  | Primary key                                  |
| sender_id   | TEXT     | Foreign key referencing students table       |
| receiver_id | TEXT     | Foreign key referencing students table       |
| content     | TEXT     | Message content                              |
| timestamp   | DATETIME | When the message was sent                    |


### Notifications
| Column           | Type     | Description                                  |
|------------------|----------|----------------------------------------------|
| notification_id  | INTEGER  | Primary key                                  |
| student_id       | TEXT     | Foreign key referencing students table       |
| type             | TEXT     | e.g., daily_checkin, chat_reminder           |
| content          | TEXT     | Message or reminder content                  |
| status           | TEXT     | sent, read, or dismissed                     |
| timestamp        | DATETIME | When the notification was created            |


# Tools/ Libraries 
- SQLite
- Pandas


# Python Scripts
`setup_db.py:`
1. Loads CSV
2. Creates and populates all 3–5 tables

`query_db.py:`
Sample matching logic (e.g., find users with 2+ shared subjects & overlapping availability)

# Matching Logic
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


# Folder Structure 
virtual-study-buddy-app/
│
├── data/                         
│   └── virtual_study_buddy_mock_data.csv
│
├── db/                           
│   └── study_buddy.db
│
├── notebooks/                   
│   └── test_setup_db.ipynb
│
├── scripts/
│   ├── setup_db.py
│   └── query_db.py ??
│
└── README.md 

# User App Flow 

# Contributors 
**Our Team consists of only Data Science Fellows:**
- Adewale Thompson
- Akisha Robinson
- Gennadii Ershov
- Jasmin Sweat
- Zahrea Franklin
- Zakiyyah Jones
- Julissa Morales

**Bloomberg Mentors:**
- Karishma Borole
- Yogesh Bhatti

# License
This project was developed solely for educational and demonstration purposes during a hackathon. We do not claim ownership of the data used; it was generated via Mockaroo(https://mockaroo.com) and used strictly to simulate a study buddy matching system.  
No real user information is stored, collected, or shared.