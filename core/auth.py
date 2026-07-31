import logging
import sqlite3
import bcrypt

DATABASE = "database/database.db"

# Child logger — inherits handlers from "cyberlab"
log = logging.getLogger("cyberlab.auth")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def user_exists(username: str) -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM users WHERE username = ? LIMIT 1",
        (username,),
    )

    exists = cursor.fetchone() is not None
    conn.close()

    return exists


def create_user(username, password, role="student") -> bool:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    hashed = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users(username, password, role) VALUES (?, ?, ?)",
            (username, hashed, role),
        )
        conn.commit()
        log.info(f"User created: {username} (role={role})")
        return True

    except sqlite3.IntegrityError:
        log.warning(f"Duplicate username rejected: {username}")
        return False

    finally:
        conn.close()


def authenticate(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password, role FROM users WHERE username = ?",
        (username,),
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        stored_hash, role = user

        if verify_password(password, stored_hash):
            log.info(f"Authentication success: {username}")
            return True, role

    log.warning(f"Authentication failed: {username}")
    return False, None
