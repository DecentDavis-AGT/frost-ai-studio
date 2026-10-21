# -*- coding: utf-8 -*-
import sqlite3
import hashlib
import os
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "frost_users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            fact_key TEXT NOT NULL,
            fact_value TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt

def register_user(username, display_name, email, password):
    username = username.strip().lower()
    email = email.strip().lower()
    display_name = display_name.strip()
    
    if len(username) < 3:
        return False, "Username kam az kam 3 characters ka ho."
    if len(password) < 4:
        return False, "Password kam az kam 4 characters ka ho."
    
    hashed_pwd, salt = hash_password(password)
    user_id = f"usr_{secrets.token_hex(6)}"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (user_id, username, display_name, email, password_hash, salt)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, display_name, email, hashed_pwd, salt))
        conn.commit()
        return True, {
            "user_id": user_id,
            "username": username,
            "display_name": display_name,
            "email": email
        }
    except sqlite3.IntegrityError as e:
        err = str(e).lower()
        if "username" in err:
            return False, "Yeh username pehle se registered hai."
        elif "email" in err:
            return False, "Yeh email pehle se registered hai."
        return False, "Account register nahi ho saka."
    finally:
        conn.close()

def login_user(username_or_email, password):
    identifier = username_or_email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, username, display_name, email, password_hash, salt
        FROM users
        WHERE username = ? OR email = ?
    ''', (identifier, identifier))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False, "Account nahi mila. Credentials check karein."
    
    user_id, username, display_name, email, stored_hash, salt = row
    test_hash, _ = hash_password(password, salt)
    
    if test_hash == stored_hash:
        return True, {
            "user_id": user_id,
            "username": username,
            "display_name": display_name,
            "email": email
        }
    return False, "Galat password! Dobara check karein."

init_db()