# database.py
import sqlite3
from datetime import datetime

def get_db_connection():
    """Create and return a new database connection"""
    return sqlite3.connect("users.db")

def init_db():
    """Initialize all database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    age INTEGER,
                    precinct_code TEXT,
                    code TEXT,
                    username TEXT UNIQUE,
                    rank TEXT,
                    badge_number TEXT UNIQUE
                )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS criminals (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    age INTEGER,
                    crime TEXT,
                    criminal_id TEXT UNIQUE,
                    emotions TEXT
                )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS emotion_logs (
                    id INTEGER PRIMARY KEY,
                    criminal_id TEXT,
                    timestamp TEXT,
                    emotion TEXT,
                    FOREIGN KEY (criminal_id) REFERENCES criminals(criminal_id)
                )''')
    
    conn.commit()
    conn.close()

def add_officer(name, age, precinct_code, code, rank, badge_number):
    """Add a new police officer to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_id = cursor.fetchone()[0] + 1
        username = f"{name}{precinct_code}{user_id}"
        cursor.execute("""INSERT INTO users 
                       (name, age, precinct_code, code, username, rank, badge_number) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                       (name, age, precinct_code, code, username, rank, badge_number))
        conn.commit()
        return username
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def verify_officer(username, code):
    """Verify police officer credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND code=?", (username, code))
    officer = cursor.fetchone()
    conn.close()
    return officer

def add_criminal(name, age, crime, criminal_id):
    """Add a new criminal to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO criminals 
                       (name, age, crime, criminal_id) 
                       VALUES (?, ?, ?, ?)""",
                       (name, age, crime, criminal_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_criminals():
    """Retrieve all criminals from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM criminals")
    criminals = cursor.fetchall()
    conn.close()
    return criminals

def get_criminal_by_id(criminal_id):
    """Get a specific criminal by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM criminals WHERE criminal_id=?", (criminal_id,))
    criminal = cursor.fetchone()
    conn.close()
    return criminal

def remove_criminal(criminal_id):
    """Remove a criminal from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM criminals WHERE criminal_id=?", (criminal_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def log_emotion(criminal_id, emotion):
    """Log an emotion detection for a criminal"""
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""INSERT INTO emotion_logs 
                   (criminal_id, timestamp, emotion) 
                   VALUES (?, ?, ?)""",
                   (criminal_id, timestamp, emotion))
    conn.commit()
    conn.close()

def get_emotion_logs(criminal_id):
    """Get all emotion logs for a criminal"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT timestamp, emotion FROM emotion_logs 
                   WHERE criminal_id=? ORDER BY timestamp""", (criminal_id,))
    logs = cursor.fetchall()
    conn.close()
    return logs

# Initialize the database
init_db()