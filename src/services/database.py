import sqlite3
import json
import uuid
from datetime import datetime
import os
import logging

import bcrypt
from src.config import ADMIN_DEFAULT_PASSWORD

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="chatbot.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=20)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _hash_password(self, password):
        """Secure bcrypt password hashing with automatic salt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, password, hashed):
        """Verify password against bcrypt hash."""
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception as e:
            logger.warning(f"Password verification failed: {e}")
            return False

    def init_db(self):
        """Creates the necessary tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # User & Session Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT,
                created_at TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at TIMESTAMP,
                last_active TIMESTAMP,
                metadata TEXT,
                active_mode TEXT DEFAULT NULL,
                FOREIGN KEY(user_id) REFERENCES users(username)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        ''')

        # Vitals & Symptoms
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                vital_type TEXT,
                value TEXT,
                unit TEXT,
                timestamp TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY(user_id) REFERENCES users(username)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                symptom_code TEXT,
                severity TEXT,
                duration TEXT, 
                timestamp TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY(user_id) REFERENCES users(username)
            )
        ''')
        
        # Prescriptions & Reminders (RESTORED)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                medicine_name TEXT,
                dosage TEXT,
                frequency TEXT,
                times TEXT,       -- JSON list of "HH:MM"
                instructions TEXT,
                created_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(username)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id INTEGER,
                scheduled_time TIMESTAMP,
                status TEXT DEFAULT 'pending', -- pending, sent, skipped
                FOREIGN KEY(prescription_id) REFERENCES prescriptions(id)
            )
        ''')

        # migrations
        try: cursor.execute("ALTER TABLE sessions ADD COLUMN active_mode TEXT DEFAULT NULL")
        except: pass
        try: cursor.execute("ALTER TABLE symptoms ADD COLUMN duration TEXT DEFAULT NULL")
        except: pass

        conn.commit()
        conn.close()

        try:
            self.create_user("admin", ADMIN_DEFAULT_PASSWORD)
        except sqlite3.IntegrityError:
            pass

    # --- User & Session Methods ---
    def create_user(self, username, password):
        password_hash = self._hash_password(password)
        now = datetime.now()
        conn = self.get_connection()
        try:
            conn.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)", (username, password_hash, now))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def verify_user(self, username, password):
        conn = self.get_connection()
        row = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if not row: return False
        if password == "google_oauth_dummy": return True # Simplified for this demo
        return self._verify_password(password, row['password_hash'])

    def create_session(self, user_id="admin", metadata=None):
        session_id = str(uuid.uuid4())
        now = datetime.now()
        conn = self.get_connection()
        conn.execute("INSERT INTO sessions (id, user_id, created_at, last_active, metadata) VALUES (?, ?, ?, ?, ?)", 
                     (session_id, user_id, now, now, json.dumps(metadata or {})))
        conn.commit()
        conn.close()
        return session_id

    def add_message(self, session_id, role, content, metadata=None):
        now = datetime.now()
        conn = self.get_connection()
        conn.execute("INSERT INTO messages (session_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                     (session_id, role, content, now, json.dumps(metadata or {})))
        conn.execute("UPDATE sessions SET last_active = ? WHERE id = ?", (now, session_id))
        conn.commit()
        conn.close()

    def get_history(self, session_id, limit=None):
        conn = self.get_connection()
        query = "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC"
        if limit: query += f" LIMIT {limit}"
        rows = conn.execute(query, (session_id,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_recent_sessions(self, user_id="admin", limit=5):
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY last_active DESC LIMIT ?", (user_id, limit)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # --- Vitals & Symptoms ---
    def add_vital(self, user_id, vital_type, value, unit, metadata=None):
        now = datetime.now()
        conn = self.get_connection()
        conn.execute("INSERT INTO vitals (user_id, vital_type, value, unit, timestamp, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                     (user_id, vital_type, value, unit, now, json.dumps(metadata or {})))
        conn.commit()
        conn.close()

    def get_vitals(self, user_id, vital_type=None, limit=5):
        conn = self.get_connection()
        query = "SELECT * FROM vitals WHERE user_id = ?"
        params = [user_id]
        
        if vital_type:
            query += " AND vital_type = ?"
            params.append(vital_type)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # --- Symptoms ---
    def add_symptom(self, user_id, symptom_code, severity, duration, metadata=None):
        now = datetime.now()
        conn = self.get_connection()
        conn.execute("INSERT INTO symptoms (user_id, symptom_code, severity, duration, timestamp, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                     (user_id, symptom_code, severity, duration, now, json.dumps(metadata or {})))
        conn.commit()
        conn.close()

    def get_recent_symptoms(self, user_id, limit=10):
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM symptoms WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_symptom_trends_summary(self, user_id, days=30):
        conn = self.get_connection()
        # Simple aggregation: count of each symptom code in last X days
        # Calculate date threshold
        # For sqlite, we can use datetime modifier
        rows = conn.execute('''
            SELECT symptom_code, COUNT(*) as count, MAX(severity) as max_severity 
            FROM symptoms 
            WHERE user_id = ? AND timestamp >= datetime('now', ?)
            GROUP BY symptom_code
        ''', (user_id, f'-{days} days')).fetchall()
        conn.close()
        return {row['symptom_code']: {'count': row['count'], 'max_severity': row['max_severity']} for row in rows}
    
    # --- Prescriptions & Reminders ---
    def add_prescription(self, user_id, medicine_name, dosage, frequency, times, instructions):
        now = datetime.now()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO prescriptions (user_id, medicine_name, dosage, frequency, times, instructions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, medicine_name, dosage, frequency, times, instructions, now))
        pres_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pres_id

    def get_active_prescriptions(self, user_id):
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM prescriptions WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC", (user_id,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def deactivate_prescription(self, pres_id):
        conn = self.get_connection()
        cursor = conn.execute("UPDATE prescriptions SET is_active = 0 WHERE id = ?", (pres_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def add_reminder(self, prescription_id, scheduled_time):
        conn = self.get_connection()
        conn.execute("INSERT INTO reminders (prescription_id, scheduled_time, status) VALUES (?, ?, 'pending')", 
                     (prescription_id, scheduled_time))
        conn.commit()
        conn.close()

    def get_upcoming_reminders(self, user_id):
        conn = self.get_connection()
        # Join with prescriptions to confirm user ownership
        rows = conn.execute('''
            SELECT r.*, p.medicine_name 
            FROM reminders r
            JOIN prescriptions p ON r.prescription_id = p.id
            WHERE p.user_id = ? AND r.scheduled_time > datetime('now') AND r.status = 'pending'
            ORDER BY r.scheduled_time ASC
        ''', (user_id,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_active_mode(self, session_id):
        conn = self.get_connection()
        row = conn.execute("SELECT active_mode FROM sessions WHERE id = ?", (session_id,)).fetchone()
        conn.close()
        return row['active_mode'] if row else None

    def set_active_mode(self, session_id, mode):
        conn = self.get_connection()
        conn.execute("UPDATE sessions SET active_mode = ? WHERE id = ?", (mode, session_id))
        conn.commit()
        conn.close()