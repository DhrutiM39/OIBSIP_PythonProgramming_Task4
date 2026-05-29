import sqlite3
import hashlib

def init_database():
    # Purpose: Create users table if not exists
    conn = sqlite3.connect("chat_app.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            created  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    # Purpose: Convert plain password to SHA256 hash
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(username, password):
    # Purpose: Save new user to database with hashed password
    if not username or not password:
        return "❌ Username and password required!"
    if len(password) < 6:
        return "❌ Password must be at least 6 characters!"
    try:
        conn = sqlite3.connect("chat_app.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return "✅ Registered successfully!"
    except sqlite3.IntegrityError:
        return "❌ Username already taken!"

def login_user(username, password):
    # Purpose: Verify username and hashed password against database
    conn = sqlite3.connect("chat_app.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )
    result = cursor.fetchone()
    conn.close()

    if not result:
        return "❌ Username not found!"
    if result[0] != hash_password(password):
        return "❌ Wrong password!"
    return "✅ Login successful!"
