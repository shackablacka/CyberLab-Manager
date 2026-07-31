import sqlite3
import logging
from datetime import datetime

from core.auth import DATABASE

log = logging.getLogger("cyberlab.modules.attendance")

def run(username: str, role: str):
    while True:
        print("\n=== Attendance ===")
        print("1. Check In")
        print("2. Check Out")
        print("3. View Attendance")
        print("0. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            check_in(username)
        elif choice == "2":
            check_out(username)
        elif choice == "3":
            view_attendance(role)
        else:
            print("[!] Invalid option.")


def get_user_id(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def check_in(username):
    user_id = get_user_id(username)
    if not user_id:
        print("[!] User not found.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Prevent double check-in (no open record)
    cursor.execute(
        "SELECT id FROM attendance WHERE user_id=? AND check_out IS NULL",
        (user_id,),
    )
    if cursor.fetchone():
        print("[!] Already checked in. Check out first.")
        conn.close()
        return

    cursor.execute(
        "INSERT INTO attendance(user_id) VALUES (?)",
        (user_id,),
    )
    conn.commit()
    conn.close()
    print(f"[+] Checked in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def check_out(username):
    user_id = get_user_id(username)
    if not user_id:
        print("[!] User not found.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM attendance WHERE user_id=? AND check_out IS NULL ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    row = cursor.fetchone()
    if not row:
        print("[!] You are not checked in.")
        conn.close()
        return

    cursor.execute(
        "UPDATE attendance SET check_out=? WHERE id=?",
        (datetime.now().isoformat(), row[0]),
    )
    conn.commit()
    conn.close()
    print("[+] Checked out.")


def view_attendance(role):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if role == "admin":
        cursor.execute(
            """SELECT a.id, u.username, a.check_in, a.check_out
               FROM attendance a JOIN users u ON a.user_id = u.id
               ORDER BY a.check_in DESC"""
        )
        rows = cursor.fetchall()
        if not rows:
            print("\nNo attendance records.")
        else:
            print("\nID | Username | Check In | Check Out")
            print("-" * 60)
            for rid, uname, ci, co in rows:
                print(f"{rid} | {uname} | {ci} | {co or 'still in'}")
    else:
        user_id = get_user_id(input("Enter username or leave blank for self: ").strip() or "self")
        if user_id == "self":
            user_id = get_user_id(input("Your username: ").strip())
        if not user_id:
            print("[!] User not found.")
            conn.close()
            return
        cursor.execute(
            """SELECT a.id, u.username, a.check_in, a.check_out
               FROM attendance a JOIN users u ON a.user_id = u.id
               WHERE a.user_id=?
               ORDER BY a.check_in DESC""",
            (user_id,),
        )
        rows = cursor.fetchall()
        if not rows:
            print("\nNo attendance records for that user.")
        else:
            print("\nID | Username | Check In | Check Out")
            print("-" * 60)
            for rid, uname, ci, co in rows:
                print(f"{rid} | {uname} | {ci} | {co or 'still in'}")

    conn.close()
