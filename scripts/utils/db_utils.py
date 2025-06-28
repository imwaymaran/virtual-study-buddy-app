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