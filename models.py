import sqlite3
import bcrypt
import json
from datetime import datetime, timedelta
from config import Config


def get_db():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5),
            description TEXT,
            emotion_tag TEXT,
            triggers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            messages TEXT NOT NULL DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS study_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            schedule_json TEXT NOT NULL,
            subjects TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS check_ins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()


# ── User helpers ─────────────────────────────────────────────────────────────

def create_user(username, email, password):
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


# ── Mood helpers ─────────────────────────────────────────────────────────────

def log_mood(user_id, score, description='', emotion_tag='', triggers=''):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO mood_logs (user_id, score, description, emotion_tag, triggers) VALUES (?, ?, ?, ?, ?)',
        (user_id, score, description, emotion_tag, triggers)
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    record_checkin(user_id)
    return log_id


def get_mood_logs(user_id, days=30):
    conn = get_db()
    cursor = conn.cursor()
    logs = cursor.execute(
        '''SELECT * FROM mood_logs WHERE user_id = ?
           AND created_at >= datetime('now', ?)
           ORDER BY created_at ASC''',
        (user_id, f'-{days} days')
    ).fetchall()
    conn.close()
    return [dict(log) for log in logs]


def get_latest_mood(user_id):
    conn = get_db()
    cursor = conn.cursor()
    log = cursor.execute(
        'SELECT * FROM mood_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(log) if log else None


# ── Chat session helpers ──────────────────────────────────────────────────────

def get_or_create_session(user_id):
    conn = get_db()
    cursor = conn.cursor()
    session = cursor.execute(
        'SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    if not session:
        cursor.execute(
            'INSERT INTO chat_sessions (user_id, messages) VALUES (?, ?)',
            (user_id, '[]')
        )
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id, []
    session = dict(session)
    conn.close()
    return session['id'], json.loads(session['messages'])


def update_session_messages(session_id, messages):
    messages = messages[-20:]   # keep last 20 for context window
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chat_sessions SET messages = ?, updated_at = datetime('now') WHERE id = ?",
        (json.dumps(messages), session_id)
    )
    conn.commit()
    conn.close()


# ── Schedule helpers ─────────────────────────────────────────────────────────

def save_schedule(user_id, schedule_json, subjects):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO study_schedules (user_id, schedule_json, subjects) VALUES (?, ?, ?)',
        (user_id, json.dumps(schedule_json), subjects)
    )
    conn.commit()
    schedule_id = cursor.lastrowid
    conn.close()
    return schedule_id


def get_latest_schedule(user_id):
    conn = get_db()
    cursor = conn.cursor()
    schedule = cursor.execute(
        'SELECT * FROM study_schedules WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
        (user_id,)
    ).fetchone()
    conn.close()
    if schedule:
        s = dict(schedule)
        s['schedule_json'] = json.loads(s['schedule_json'])
        return s
    return None


# ── Check-in helpers ─────────────────────────────────────────────────────────

def record_checkin(user_id):
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cursor = conn.cursor()
    existing = cursor.execute(
        'SELECT id FROM check_ins WHERE user_id = ? AND date = ?',
        (user_id, today)
    ).fetchone()
    if not existing:
        cursor.execute(
            'INSERT INTO check_ins (user_id, date) VALUES (?, ?)',
            (user_id, today)
        )
        conn.commit()
    conn.close()


def get_checkin_streak(user_id):
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute(
        'SELECT date FROM check_ins WHERE user_id = ? ORDER BY date DESC LIMIT 30',
        (user_id,)
    ).fetchall()
    conn.close()
    if not rows:
        return 0
    streak = 0
    today = datetime.now().date()
    for i, row in enumerate(rows):
        check_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
        if check_date == today - timedelta(days=i):
            streak += 1
        else:
            break
    return streak


def get_checkin_count(user_id, days=30):
    conn = get_db()
    cursor = conn.cursor()
    count = cursor.execute(
        '''SELECT COUNT(*) as cnt FROM check_ins WHERE user_id = ?
           AND date >= date('now', ?)''',
        (user_id, f'-{days} days')
    ).fetchone()
    conn.close()
    return count['cnt'] if count else 0
