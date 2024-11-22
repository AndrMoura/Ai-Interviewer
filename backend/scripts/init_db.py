import sqlite3

from passlib.context import CryptContext
from ..constants import DATABASE_NAME, ROLE_CFG
from ..login import hash_password


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_USERS = [
    {"username": "testuser", "password": "password123", "role": "user"},
    {"username": "adminuser", "password": "adminpassword", "role": "admin"},
]


def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """
        )
        conn.commit()
        for user in DEFAULT_USERS:
            try:
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (user["username"], hash_password(user["password"]), user["role"]),
                )
            except sqlite3.IntegrityError:
                print(f"User {user['username']} already exists, skipping.")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interviews (
                session_id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                role_description TEXT,
                messages TEXT,
                evaluation TEXT
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS role_settings (
                role TEXT PRIMARY KEY,
                custom_questions TEXT,
                job_description TEXT
            )
        """
        )
        for role, config in ROLE_CFG.items():
            cursor.execute(
                """
                INSERT OR IGNORE INTO role_settings (role, custom_questions, job_description)
                VALUES (?, ?, ?)
            """,
                (
                    role,
                    "Ask about their favorite programming language\nAsk about their pets!",
                    config,
                ),
            )
        conn.commit()


if __name__ == "__main__":
    init_db()
