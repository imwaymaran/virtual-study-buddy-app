from flask import Blueprint, render_template, request, redirect
import sys
import os
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from scripts.utils.db_utils import get_or_create_subject, get_next_student_id
from scripts.utils.time_utils import STUDY_TIME_RANGES, shift_to_utc, shift_to_local, get_utc_day
from scripts.matching_logic import default_match, custom_match

from config import DB_PATH

main = Blueprint("main", __name__)


@main.route("/form", methods=["GET", "POST"])
def register():
    # POST: insert info to db
    if request.method == "POST":
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name") or ""
        last_name = request.form.get("last_name")
        student_name = " ".join(
            part.strip().title() for part in [first_name, middle_name, last_name] if part and part.strip()
        )
        gpa_raw = request.form.get("GPA")
        try:
            gpa = float(gpa_raw) if gpa_raw else None
        except ValueError:
            gpa = None

        experience_level = request.form.get("experience_level")
        study_style = request.form.get("study_style")
        personality_type = request.form.get("personality_type") or None

        #This adds tutor or tutee to the database
        "study_buddy_type" = request.form.get("study_buddy_type")

        timezone = request.form.get("timezone")
        utc_offset = int(timezone.replace("UTC", ""))

        study_times = request.form.get("study_times")
        local_start, local_end = STUDY_TIME_RANGES.get(study_times)
        utc_start_time = shift_to_utc(local_start, utc_offset)
        utc_end_time = shift_to_utc(local_end, utc_offset)

        days_of_wk_avail = request.form.getlist("days_of_wk_avail[]")
        
        subjects = request.form.getlist("preferred_subjects[]")
        other_subject = request.form.get("other_subject")
        if other_subject:
            subjects.append(other_subject.strip().title())

        student_id = get_next_student_id()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (
                    student_id, student_name, personality_type, study_style, utc_offset,
                    experience_level, GPA, utc_start_time, utc_end_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                student_name,
                personality_type,
                study_style,
                utc_offset,
                experience_level,
                gpa,
                utc_start_time,
                utc_end_time
            ))
            
            for day in days_of_wk_avail:
                cursor.execute(
                    'INSERT OR IGNORE INTO study_days (student_id, day) VALUES (?, ?)',
                    (student_id, day)
                )
                utc_day = get_utc_day(day, local_start, utc_offset)
                cursor.execute(
                    'INSERT OR IGNORE INTO utc_study_days (student_id, utc_day) VALUES (?, ?)',
                    (student_id, utc_day)
                )

            for subject_name in subjects:
                subject_id = get_or_create_subject(cursor, subject_name)
                cursor.execute(
                    "INSERT OR IGNORE INTO student_subjects (student_id, subject_id) VALUES (?, ?)",
                    (student_id, subject_id)
                )

        return redirect(f"/account/{student_id}")

    # GET: pull subjects list from db
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT subject_name FROM subjects ORDER BY subject_name")
        subjects = [row[0] for row in cursor.fetchall()]

    return render_template("form.html", subjects=subjects)


@main.route("/account/<student_id>")
def account(student_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT student_name, personality_type, study_style, utc_offset,
                   experience_level, GPA, utc_start_time, utc_end_time
            FROM students
            WHERE student_id = ?
        """, (student_id,))
        student = cursor.fetchone()

        cursor.execute("SELECT day FROM study_days WHERE student_id = ?", (student_id,))
        study_days = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT subject_name
            FROM subjects
            JOIN student_subjects ON subjects.subject_id = student_subjects.subject_id
            WHERE student_subjects.student_id = ?
        """, (student_id,))
        subjects = [row[0] for row in cursor.fetchall()]

    # Convert UTC to local
    utc_start, utc_end = student[6], student[7]
    utc_offset = int(student[3])
    local_start = shift_to_local(utc_start, utc_offset)
    local_end = shift_to_local(utc_end, utc_offset)

    return render_template(
        "account.html",
        student=student,
        study_days=study_days,
        subjects=subjects,
        local_start=local_start,
        local_end=local_end
    )

@main.route('/match/<student_id>', methods=['GET', 'POST'])
def match(student_id):
    if request.method == 'GET':
        return render_template('match_form.html', student_id=student_id)

    # Load student profiles dynamically from database or static source
    student_profiles = load_student_profiles()  # This must return a dict keyed by student_id

    match_mode = request.form.get('mode')

    if match_mode == 'default':
        matches = default_match(student_id, student_profiles)
    else:
        preferences = {
            'subjects': 'subjects' in request.form,
            'days': 'days' in request.form,
            'time': 'time' in request.form,
            'style': 'style' in request.form,
            'GPA': 'GPA' in request.form,
            'personality': 'personality' in request.form,
        }
        matches = custom_match(student_id, preferences, student_profiles)

    return render_template('match_results.html', student_id=student_id, matches=matches)
