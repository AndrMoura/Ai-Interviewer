import json
import sqlite3
from .constants import DATABASE_NAME


def get_role_settings(role: str):
    """Fetch interview settings for a specific role."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT custom_questions, job_description
            FROM role_settings
            WHERE role = ?
            """,
            (role,),
        )
        result = cursor.fetchone()
        return result if result else (None, None)


def save_interview_to_db(session_id, role, role_description, messages, evaluation):
    """Save a new interview to the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO interviews (session_id, role, role_description, messages, evaluation)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    role,
                    role_description,
                    json.dumps(messages),
                    json.dumps(evaluation),
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error saving interview: {e}")


def create_role_to_db(role: str, custom_questions, job_description):
    """Add or update a role in the role_settings table."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO role_settings (role, custom_questions, job_description)
                VALUES (?, ?, ?)
                """,
                (role, custom_questions, job_description),
            )
            conn.commit()
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Role '{role}' already exists.") from e
    except Exception as e:
        raise ValueError(f"Error occurred while creating the role: {str(e)}") from e


def get_interviews_from_db():
    """Retrieve a list of all interviews."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, messages FROM interviews")

        return [
            {
                "session_id": row[0],
                "messages": (json.loads(row[1]) if row[1] else "Empty Interview"),
            }
            for row in cursor.fetchall()
        ]


def create_interview_role_to_db(
    session_id: str, role: str, role_description: str, messages, evaluation
):
    """Save an interview with role details into the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO interviews (session_id, role, role_description, messages, evaluation)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    role,
                    role_description,
                    json.dumps(messages),
                    json.dumps(evaluation),
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error creating interview: {e}")


def get_interview_detail_from_db(session_id):
    """Fetch detailed information for a specific interview."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT role, role_description, messages, evaluation
            FROM interviews WHERE session_id = ?
            """,
            (session_id,),
        )
        result = cursor.fetchone()
        if not result:
            return None
        return {
            "session_id": session_id,
            "role": result[0],
            "role_description": result[1],
            "messages": json.loads(result[2]),
            "evaluation": json.loads(result[3]),
        }


def get_user_from_db(username):
    """Retrieve a user by username."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT username, password, role
            FROM users
            WHERE username = ?
            """,
            (username,),
        )
        row = cursor.fetchone()
        if row:
            return {"username": row[0], "password": row[1], "role": row[2]}
    return None


async def get_roles_db():
    """Retrieve all roles with their job descriptions."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, job_description, custom_questions FROM role_settings")
        roles_with_description = [
            {
                "role": row[0],
                "job_description": row[1] if row[1] else "No description available",
                "custom_questions": row[2] if row[2] else "No custom questions available",
            }
            for row in cursor.fetchall()
        ]
    return roles_with_description


async def get_role_details_db(role: str):
    """Fetch role details from the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT role, custom_questions, job_description
            FROM role_settings
            WHERE role = ?
            """,
            (role,),
        )
        row = cursor.fetchone()
        if row:
            return {
                "role": row[0],
                "custom_questions": row[1],
                "job_description": row[2],
            }
        return None


async def update_role_details_db(role: str, role_data: dict):
    """Update role details in the database."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE role_settings
            SET custom_questions = ?, job_description = ?
            WHERE role = ?
            """,
            (role_data["custom_questions"], role_data["job_description"], role),
        )
        conn.commit()

        if cursor.rowcount == 0:
            return None
        return True
