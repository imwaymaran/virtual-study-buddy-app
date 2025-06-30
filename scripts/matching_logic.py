#!/usr/bin/env python
# coding: utf-8

# # Virtual Study Buddy – Matching Algorithm
# 
# ## Virtual Study Buddy App – Matching Logic Overview
# 
# This notebook contains the core matching algorithms for the Virtual Study Buddy App, which connects students based on shared academic interests, availability, and learning preferences. The goal is to foster meaningful peer-to-peer support through tailored match suggestions.
# 
# We offer two matching modes:
# 
# ### Default Mode: Tutor–Learner Matching
# In this model, students are assigned a role based on their GPA:
# - **Tutors**: Students with a GPA ≥ 3.5  
# - **Learners**: Students with a GPA < 3.5
# 
# Learners are automatically paired with tutors who:
# - Specialize in overlapping subjects
# - Share at least two study days with 60+ minutes of time overlap
# - Have a compatible study style
# 
# This mode generates the top 3 tutor recommendations per learner using a standardized scoring system.
# 
# ---
# 
# ### Custom Mode: Preference-Based Matching
# This mode allows learners to set their own matching priorities via selectable preferences, such as:
# - Shared subjects  
# - Matching availability (days and/or time)  
# - Study style compatibility  
# - Similar GPA goals  
# - Personality alignment
# 
# Users can emphasize what's most important to them, and the algorithm scores and returns the best tutor matches accordingly.
# 
# ---
# 
# All results are formatted for easy integration into a front-end application or exportable reports. All matching results in this notebook are structured as flat pandas DataFrames or lists of dictionaries, with clearly labeled columns such as student_id, match_id, subject_overlap, and total_score. This format ensures compatibility with:
# 
# - Export tools like .to_csv() or .to_json() for reporting or analysis
# 
# - Front-end applications via simple API responses (e.g., converting to JSON for use in JavaScript or Flask-based interfaces)
# 

# ## Set Up

# ### Import Libraries

# In[110]:


# Import Libraries
import sqlite3 
import pandas as pd
from datetime import datetime


# ### Connect to Database

# In[111]:


# Connect to the SQLite database
# Make sure the path is correct. Adjust the path as needed.
database = ('../data/processed/study_buddy.db')
conn = sqlite3.connect(database)


# ### Load Data

# In[112]:


# Load tables into DataFrames
df_students = pd.read_sql("SELECT * FROM students", conn)
df_subjects = pd.read_sql("SELECT * FROM subjects", conn)
df_student_subjects = pd.read_sql("SELECT * FROM student_subjects", conn)
df_study_days = pd.read_sql("SELECT * FROM study_days", conn)
df_utc_study_days = pd.read_sql("SELECT * FROM utc_study_days", conn)


# ### Time Overlap Utility Function
# 
# This function, `has_time_overlap`, checks whether two time ranges (student availability windows) overlap by at least a minimum number of minutes (default: 60 minutes). 
# 
# It is used to ensure that potential matches not only have shared days but also have enough overlapping availability to realistically meet.
# 
# **Parameters:**
# - `start1`, `end1`: First student's availability window.
# - `start2`, `end2`: Second student's availability window.
# - `min_overlap_minutes`: Minimum required overlap in minutes (default is 30).
# 
# **Returns:**
# - `True` if the time windows overlap by at least the specified duration.
# - `False` otherwise.
# 

# In[113]:


# Utility function to check if two time ranges overlap by at least 60 minutes
def get_time_overlap_minutes(start1, end1, start2, end2, min_overlap_minutes=30):
    fmt = "%H:%M"
    s1, e1 = datetime.strptime(start1, fmt), datetime.strptime(end1, fmt)
    s2, e2 = datetime.strptime(start2, fmt), datetime.strptime(end2, fmt)
    latest_start = max(s1, s2)
    earliest_end = min(e1, e2)
    overlap = (earliest_end - latest_start).total_seconds() / 60  # in minutes
    return max(0, overlap)


# ## Default Mode Matching Logic
# 
# This section defines the automatic matching logic used by the Virtual Study Buddy App to pair learners with compatible tutors. This mode does not require user input and is ideal for quickly generating tutor recommendations for all learners.
# 
# **Matching Criteria:**
# 1. Role-Based Filtering
# Only students with a GPA of 3.5 or higher are considered tutors. The default logic matches learners (below 3.5 GPA) exclusively with these tutors.
# 
# 2. **Subject Overlap**
# Matches are only considered if the learner and tutor share at least one subject of interest — ensuring the tutor is qualified to help in the learner’s target area.
# 
# 3. **Availability (Days & Time)**
# The learner and tutor must share at least 2 study days, with a minimum of 60 minutes of overlapping UTC availability.
# 
# 4. **Study Style Compatibility**
# Learners are more likely to be paired with tutors who share a similar study style, increasing the chance of a productive match.
# 
# **Output:**
# Each learner receives a list of their top 3 tutor matches based on a scoring system that considers subject relevance, shared time, and compatibility traits. This approach offers a structured yet automated way to improve academic performance through peer support.

# ### Create subject name mapping and build student profiles

# In[114]:


# Create a subject_id -> subject_name dictionary
subject_map = df_subjects.set_index("subject_id")["subject_name"].to_dict()

# Replace subject_id with subject_name in student_subjects table
df_student_subjects["subject_name"] = df_student_subjects["subject_id"].map(subject_map)

# Build a profile for each student with their subjects, availability, and study style
student_profiles = {}

for sid in df_students["student_id"]:
    subjects = set(df_student_subjects[df_student_subjects["student_id"] == sid]["subject_name"])
    days = set(df_utc_study_days[df_utc_study_days["student_id"] == sid]["utc_day"])
    style = df_students[df_students["student_id"] == sid]["study_style"].values[0]
    personality = df_students[df_students["student_id"] == sid]["personality_type"].values[0] 
    gpa_goal = df_students[df_students["student_id"] == sid]["GPA"].values[0] 
    start_time = df_students[df_students["student_id"] == sid]["utc_start_time"].values[0]
    end_time = df_students[df_students["student_id"] == sid]["utc_end_time"].values[0]
    
    # Assign role based on GPA
    role = "tutor" if gpa_goal >= 3.5 else "learner"
    
    student_profiles[sid] = {
        "subjects": subjects,
        "days": days,
        "style": style,
        "personality": personality,
        "GPA": gpa_goal,
        "start_time": start_time,
        "end_time": end_time,
        "role": role
    }


# In[115]:


# Test to make sure it works
from collections import Counter
Counter([profile["role"] for profile in student_profiles.values()])  # Check the distribution of roles


# ### Compute match scores

# In[116]:


# Match each student with others who share availability, subjects, days, time and study style
match_results = []

# Get list of all student IDs
student_ids = df_students["student_id"].tolist()

# Loop through each student and compare with others
for sid in student_ids:
    if student_profiles[sid]["role"] != "learner":
        continue  # Only learners receive matches
     
    # Get the current student's profile
    sid_subjects = student_profiles[sid]["subjects"]
    sid_days = student_profiles[sid]["days"]
    sid_start_time = student_profiles[sid]["start_time"]
    sid_end_time = student_profiles[sid]["end_time"]
    sid_style = student_profiles[sid]["style"]

    # Initialize match details, loop through potential matches
    for partner_id in student_ids or student_profiles[partner_id]["role"] != "tutor":
        if sid == partner_id:
            continue  # Skip matching with self and non-tutors

        # Get the partner's profile
        partner_subjects = student_profiles[partner_id]["subjects"]
        partner_days = student_profiles[partner_id]["days"]
        partner_style = student_profiles[partner_id]["style"]
        partner_start_time = student_profiles[partner_id]["start_time"]
        partner_end_time = student_profiles[partner_id]["end_time"]

        # Calculate matches/overlaps
        subject_match = len(sid_subjects & partner_subjects)
        day_match = len(sid_days & partner_days)
        style_match = 1 if sid_style == partner_style else 0

        # Time overlap: checks if they overlap for at least 60 minutes
        time_overlap = get_time_overlap_minutes(sid_start_time, sid_end_time, partner_start_time, partner_end_time)

        # Total score (only count time overlap if True)
        total_score = subject_match + day_match + style_match + (1 if time_overlap else 0)

        # Save Match Result
        match_results.append({
            "student_id": sid, #Learner's ID
            "potential_match": partner_id, # Tutor's ID
            "subject_overlap": subject_match,
            "day_overlap": day_match,
            "time_overlap": time_overlap,
            "style_match": style_match,
            "total_score": total_score
        })


# ### Convert to DataFrame and get top matches

# In[117]:


# Convert match results to a DataFrame
match_df = pd.DataFrame(match_results)

# Sort matches by student and by highest score
top_matches = match_df.sort_values(by=["student_id", "total_score"], ascending=[True, False])

# Show top 3 matches for each student
top_matches.groupby("student_id").head()


# ## Custom Matching Based on User Preferences 
# This section introduces a more targeted matching logic tailored to the peer-tutoring model. Students are divided into learners (GPA below 3.5) and tutors (GPA 3.5 or above). Learners can be matched with available tutors based on selected preferences.
# 
# **Key Features:**
# - Only learners can request matches.
# 
# - Only tutors (students with a GPA ≥ 3.5) are eligible as match partners.
# 
# - Matching is fully customizable, based on selected criteria like availability, study style, GPA goals, and more.
# 
# **Core Functions:**
# - `custom_match(user_id, preferences)`:
# For a given learner, this function ranks tutor matches by score based on criteria such as:
#     - Overlapping subjects
#     - Shared availability (days + time)
#     - Matching study styles
#     - GPA alignment
#     - Personality compatibility
# 
# -`generate_all_custom_matches(preferences)`:
# Applies `custom_match` across the entire dataset to return top-ranked tutor matches for each learner.
# 
# **How It Works:**
# Matching preferences are passed in as a dictionary of booleans ({ 'subjects': True, 'days': False, ... }). The match score increases with each matching trait, creating a list of tutor recommendations per learner. This logic is ready to connect to a frontend interface where students can select what matters most to them (via checkboxes).
# 
# The final results are returned as a DataFrame of top matches per learner, making them easy to visualize, export, or analyze.
# 
# 

# In[118]:


# Function to generate custom matches for a single user based on selected preferences
def custom_match(user_id, preferences):
    """
    Returns the top 3 tutor matches for a given learner based on selected matching preferences.

    This function compares the learner (identified by `user_id`) against all users labeled as "tutors" 
    in the student_profiles dataset. It calculates a match score for each potential tutor by comparing 
    attributes such as subject overlap, shared availability, study style, GPA goals, and personality.

    Only users with the role "learner" can be matched, and only users with the role "tutor" are considered
    as valid matches.

    Parameters:
        user_id (int): The learner's unique ID to find tutor matches for.
        preferences (dict): A dictionary specifying which criteria to include in the match score.
            Keys can include:
                - 'subjects': bool — Compare overlapping subjects (1 point per shared subject)
                - 'days': bool — Add 1 point for at least 2 overlapping availability days
                - 'time': bool — Add 1 point for 60+ minutes of overlapping time (only if 'days' is also True)
                - 'style': bool — Add 1 point if study styles match
                - 'GPA': bool — Add 1 point if GPA goals match
                - 'personality': bool — Add 1 point if personalities match

    Returns:
        List[dict]: A list of up to 3 matched tutors, sorted by descending total match score.
            Each dictionary includes:
                - 'student_id': ID of the learner
                - 'match_id': ID of the matched tutor
                - 'subject_overlap': Number of shared subjects
                - 'day_overlap': Count of overlapping available days
                - 'time_overlap_minutes': Minutes of time overlap (if evaluated)
                - 'style_match': Boolean, study style match
                - 'goal_match': Boolean, GPA match
                - 'personality_match': Boolean, personality match
                - 'total_score': Sum of points from all active criteria
    """

    # Check if user exists in the student profiles
    if user_id not in student_profiles:
        print(f"User {user_id} not found.")
        return pd.DataFrame()

    # Extract user profile details
    user_profile = student_profiles[user_id]
    if user_profile["role"] != "learner":
        print(f"User {user_id} is not a learner. Only learners can receive tutor matches.")
        return []

    user_subjects = user_profile['subjects']
    user_days = user_profile['days']
    user_start_time = user_profile['start_time']
    user_end_time = user_profile['end_time']
    user_style = user_profile['style']
    user_goal = user_profile.get('GPA', None) 
    user_personality = user_profile['personality'] 

    results = []

    # Loop through all other students to find matches
    for partner_id, partner in student_profiles.items():
        if partner_id == user_id or partner["role"] != "tutor":
            continue  # Skip self and non-tutors

        # Initialize match details   
        score = 0 
        match_details = {}

        # Subject Match
        if preferences.get('subjects'):
            subject_overlap = len(user_subjects & partner["subjects"])
            score += subject_overlap
            match_details["subject_overlap"] = subject_overlap
        else:
            match_details["subject_overlap"] = 0

        # Days + Time overlap match (combined logic)
        if preferences.get('days'):
            common_days = user_days & partner["days"]
            match_details["day_overlap"] = list(common_days)
            if len(common_days) >= 2:  # Require at least 2 common days
                score += 1
                if preferences.get("time"):
                    overlap_minutes = get_time_overlap_minutes(
                        user_start_time, user_end_time,
                        partner["start_time"], partner["end_time"]
                    )
                    match_details["time_overlap"] = overlap_minutes
                    if overlap_minutes >= 60:
                        score += 1
                else:
                    match_details["time_overlap"] = None
            else:
                match_details["time_overlap"] = None
        else:
            match_details["day_overlap"] = []
            match_details["time_overlap"] = None

        # Study style match
        if preferences.get('style'):
            style_match = user_style == partner["style"]
            score += int(style_match)  # Use int() to convert boolean to 1 or 0
            match_details["style_match"] = style_match
        else:
            match_details["style_match"] = False

        # GPA match
        if preferences.get('GPA'):
            gpa_match = user_goal == partner.get("GPA", None)
            score += int(gpa_match)
            match_details["goal_match"] = gpa_match
        else:
            match_details["goal_match"] = False

        # Personality match
        if preferences.get('personality'):
            personality_match = user_personality == partner["personality"]
            score += int(personality_match)
            match_details["personality_match"] = personality_match
        else:
            match_details["personality_match"] = False

        results.append({
            'student_id': user_id,
            'match_id': partner_id,
            'subject_overlap': match_details["subject_overlap"],
            'day_overlap': len(match_details["day_overlap"]) if match_details["day_overlap"] else 0,
            'time_overlap_minutes': match_details["time_overlap"],  
            'style_match': match_details["style_match"],
            'goal_match': match_details["goal_match"],
            'personality_match': match_details["personality_match"],
            'total_score': score
        })

    # Return the top 3 matches sorted by score
    sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
    return sorted_results[:3]


# In[119]:


# Function to generate top matches for all users using custom preferences
def generate_all_custom_matches(preferences):
    """
    Applies the custom_match function to all students in the dataset.
    
    Args:
        preferences (dict): Matching preferences selected by user.
        
    Returns:
        DataFrame of all top matches across users.
    """
    all_matches = []

    for user_id, profile in student_profiles.items():
        if profile["role"] != "learner":
            continue # Skip non-learners
        matches = custom_match(user_id, preferences)
        all_matches.extend(matches)

    return pd.DataFrame(all_matches)


# In[120]:


# Define sample user preferences for matching
user_preferences = {
    'subjects': True,
    'days': True,
    'time': True,
    'style': True,
    'GPA': True, 
    'personality': True
}

# Generate top matches for all users
custom_matches_df = generate_all_custom_matches(user_preferences)

# Display the result
custom_matches_df


# ### Understanding the Matching Results
# 
# - **subject_overlap**: Number of shared subjects between the student and their match.
# - **day_overlap**: Number of overlapping study days (both are available on Monday, Wednesday, Friday = 3).
# - **time_overlap_minutes**: Shows the number of minutes that the students' study times overlap **only if** they share **at least two common days** and the `time` preference is enabled.
#     - If **`NaN`**, this means:
#         - Either the students do **not** have at least two common days, or
#         - The user did **not** enable time overlap as a preference.
# - **style_match**, **goal_match**, and **personality_match**: Booleans indicating whether the respective attributes matched.
# - **total_score**: A cumulative score based on the number of matching criteria (including subject count, day overlap, and time overlap if applicable).
# 
# **Note**: Time overlap is only considered if there are at least **two common days**. This was done to reduce false positives and create more meaningful matches.
# 
