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
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT,
                created_at TIMESTAMP
            )
        ''')

        # Sessions Table (with active_mode for per-user state)
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
        
        # Migration: Add active_mode column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE sessions ADD COLUMN active_mode TEXT DEFAULT NULL")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Messages Table
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

        # Vitals Table
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
        
        # Symptoms Table (New)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                symptom_code TEXT,   -- e.g. "pain.head.temporal"
                severity TEXT,       -- e.g. "high", "medium", "low"
                duration TEXT,       -- e.g. "3 days", "2 hours"
                timestamp TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY(user_id) REFERENCES users(username)
            )
        ''')
        
        # Migration: Add duration column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE symptoms ADD COLUMN duration TEXT DEFAULT NULL")
        except sqlite3.OperationalError:
            pass  # Column already exists

        conn.commit()
        conn.close()

        # Create default admin if not exists (using env var for security)
        try:
            self.create_user("admin", ADMIN_DEFAULT_PASSWORD)
        except sqlite3.IntegrityError:
            pass  # Already exists

    def create_user(self, username, password):
        """Creates a new user with hashed password."""
        password_hash = self._hash_password(password)
        now = datetime.now()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, password_hash, now)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def verify_user(self, username, password):
        """Verifies a user's credentials using bcrypt."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return False
        return self._verify_password(password, row['password_hash'])

    def create_session(self, user_id="admin", metadata=None):
        """Creates a new session and returns its ID."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, user_id, created_at, last_active, metadata) VALUES (?, ?, ?, ?, ?)",
            (session_id, user_id, now, now, json.dumps(metadata or {}))
        )
        conn.commit()
        conn.close()
        return session_id

    def add_message(self, session_id, role, content, metadata=None):
        """Adds a message to the database."""
        now = datetime.now()
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert message
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, now, json.dumps(metadata or {}))
        )
        
        # Update session last_active
        cursor.execute(
            "UPDATE sessions SET last_active = ? WHERE id = ?",
            (now, session_id)
        )
        
        conn.commit()
        conn.close()

    def get_history(self, session_id, limit=None):
        """Retrieves chat history for a session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC"
        params = [session_id]
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Return as list of dicts
        return [dict(row) for row in rows]

    def get_recent_sessions(self, user_id="admin", limit=5):
        """Returns the most recent sessions for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM sessions WHERE user_id = ? ORDER BY last_active DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_vital(self, user_id, vital_type, value, unit, metadata=None):
        """Adds a health metric to the database."""
        now = datetime.now()
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO vitals (user_id, vital_type, value, unit, timestamp, metadata) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, vital_type, value, unit, now, json.dumps(metadata or {}))
        )
        
        conn.commit()
        conn.close()

    def get_vitals(self, user_id, vital_type=None, limit=10):
        """Retrieves recent vitals for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM vitals WHERE user_id = ?"
        params = [user_id]
        
        if vital_type:
            query += " AND vital_type = ?"
            params.append(vital_type)
            
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_symptom(self, user_id, symptom_code, severity, duration=None, metadata=None):
        """Adds a normalized symptom to the database with optional duration."""
        now = datetime.now()
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO symptoms (user_id, symptom_code, severity, duration, timestamp, metadata) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, symptom_code, severity, duration, now, json.dumps(metadata or {}))
        )
        
        conn.commit()
        conn.close()

    def get_recent_symptoms(self, user_id, limit=5):
        """Retrieves recent normalized symptoms."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM symptoms WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # -------------------------------------------------------------------------
    # SYMPTOM TREND ANALYSIS METHODS
    # -------------------------------------------------------------------------
    
    def get_symptom_history(self, user_id, days=90):
        """Get complete symptom history for the past N days."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM symptoms 
               WHERE user_id = ? AND timestamp >= datetime('now', ?)
               ORDER BY timestamp DESC""",
            (user_id, f'-{days} days')
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_symptom_frequency(self, user_id, symptom_code, days=30):
        """Count how many times a specific symptom has occurred in N days."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT COUNT(*) as count FROM symptoms 
               WHERE user_id = ? AND symptom_code LIKE ? AND timestamp >= datetime('now', ?)""",
            (user_id, f'{symptom_code}%', f'-{days} days')
        )
        row = cursor.fetchone()
        conn.close()
        return row['count'] if row else 0

    def detect_recurring_symptoms(self, user_id, days=30, min_occurrences=2):
        """Find symptoms that occur more than min_occurrences times."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT symptom_code, COUNT(*) as count, 
                      MAX(severity) as max_severity,
                      MIN(timestamp) as first_occurrence,
                      MAX(timestamp) as last_occurrence
               FROM symptoms 
               WHERE user_id = ? AND timestamp >= datetime('now', ?)
               GROUP BY symptom_code
               HAVING count >= ?
               ORDER BY count DESC""",
            (user_id, f'-{days} days', min_occurrences)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def detect_worsening_trends(self, user_id, days=30):
        """Detect symptoms where severity has increased over time.
        
        Returns symptoms where later occurrences have higher severity.
        Severity ranking: low=1, medium=2, high=3, unknown=0
        """
        severity_map = {'low': 1, 'medium': 2, 'high': 3, 'unknown': 0}
        
        # Get all symptoms grouped by code
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT symptom_code, severity, timestamp FROM symptoms 
               WHERE user_id = ? AND timestamp >= datetime('now', ?)
               ORDER BY symptom_code, timestamp ASC""",
            (user_id, f'-{days} days')
        )
        rows = cursor.fetchall()
        conn.close()
        
        # Group by symptom code
        symptom_history = {}
        for row in rows:
            code = row['symptom_code']
            if code not in symptom_history:
                symptom_history[code] = []
            symptom_history[code].append({
                'severity': row['severity'],
                'severity_score': severity_map.get(row['severity'].lower(), 0),
                'timestamp': row['timestamp']
            })
        
        # Detect worsening (last severity > first severity)
        worsening = []
        for code, history in symptom_history.items():
            if len(history) >= 2:
                first_score = history[0]['severity_score']
                last_score = history[-1]['severity_score']
                if last_score > first_score:
                    worsening.append({
                        'symptom_code': code,
                        'occurrences': len(history),
                        'first_severity': history[0]['severity'],
                        'last_severity': history[-1]['severity'],
                        'trend': 'worsening'
                    })
        
        return worsening

    def get_symptom_trends_summary(self, user_id, days=30):
        """Get a complete trends summary for the medical agent context."""
        recurring = self.detect_recurring_symptoms(user_id, days)
        worsening = self.detect_worsening_trends(user_id, days)
        recent = self.get_recent_symptoms(user_id, limit=10)
        
        return {
            'recurring_symptoms': recurring,
            'worsening_trends': worsening,
            'recent_symptoms': recent,
            'total_symptoms_logged': len(self.get_symptom_history(user_id, days))
        }

    def get_active_mode(self, session_id):
        """Gets the active mode for a session."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT active_mode FROM sessions WHERE id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row['active_mode'] if row else None

    def set_active_mode(self, session_id, mode):
        """Sets the active mode for a session (e.g., 'MEDICAL', None)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sessions SET active_mode = ? WHERE id = ?",
            (mode, session_id)
        )
        conn.commit()
        conn.close()