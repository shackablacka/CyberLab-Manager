import getpass
import sqlite3
import logging

from core.auth import hash_password, DATABASE

log = logging.getLogger("cyberlab.modules.users")

def run(username: str, role: str):
    """User management menu."""
    while True:
        print("\n=== User Management ===")
        print("1. List Users")
        print("2. Create User")
        print("3. Update User Role")
        print("4. Reset User Password")
        print("5. Delete User")
        print("0. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            list_users()
        elif choice == "2":
            create_user()
        elif choice == "3":
            update_user_role()
        elif choice == "4":
            reset_password()
        elif choice == "5":
            delete_user()
        else:
            print("[!] Invalid option.")


def get_all_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows


def list_users():
    users = get_all_users()
    if not users:
        print("\nNo users found.")
        return
    print("\nID | Username | Role | Created At")
    print("-" * 40)
    for uid, uname, role, created in users:
        print(f"{uid} | {uname} | {role} | {created}")


def create_user():
    username = input("New username: ").strip()
    if not username:
        print("[!] Username cannot be empty.")
        return

    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("[!] Passwords do not match.")
        return

    role = input("Role (student/instructor/admin): ").strip().lower()
    if role not in ("student", "instructor", "admin"):
        print("[!] Invalid role.")
        return

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users(username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role),
        )
        conn.commit()
        conn.close()
        log.info("User created: %s", username)
        print(f"[+] User '{username}' created.")
    except sqlite3.IntegrityError:
        print("[!] Username already exists.")


def update_user_role():
    username = input("Username to update: ").strip()
    new_role = input("New role (student/instructor/admin): ").strip().lower()
    if new_role not in ("student", "instructor", "admin"):
        print("[!] Invalid role.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role=? WHERE username=?", (new_role, username))
    conn.commit()
    if cursor.rowcount == 0:
        print("[!] User not found.")
    else:
        print(f"[+] Role updated for '{username}'.")
    conn.close()


def reset_password():
    username = input("Username to reset: ").strip()
    new_password = getpass.getpass("New password: ")
    confirm = getpass.getpass("Confirm password: ")
    if new_password != confirm:
        print("[!] Passwords do not match.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password=? WHERE username=?",
        (hash_password(new_password), username),
    )
    conn.commit()
    if cursor.rowcount == 0:
        print("[!] User not found.")
    else:
        print(f"[+] Password reset for '{username}'.")
    conn.close()


def delete_user():
    username = input("Username to delete: ").strip()
    confirm = input(f"Are you sure you want to delete '{username}'? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("[!] Cancelled.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    if cursor.rowcount == 0:
        print("[!] User not found.")
    else:
        print(f"[+] User '{username}' deleted.")
    conn.close()
