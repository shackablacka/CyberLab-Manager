import sqlite3
import logging
from core.auth import DATABASE

log = logging.getLogger("cyberlab.modules.reports")

def run(username: str, role: str):
    while True:
        print("\n=== Reports ===")
        print("1. Asset Status Report")
        print("2. Borrowing Summary")
        print("3. Attendance Summary")
        print("0. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            asset_report()
        elif choice == "2":
            borrowing_summary()
        elif choice == "3":
            attendance_summary()
        else:
            print("[!] Invalid option.")


def asset_report():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, COUNT(*) FROM assets GROUP BY status"
    )
    rows = cursor.fetchall()
    print("\n=== Asset Status Report ===")
    print("Status        | Count")
    print("-" * 25)
    for status, count in rows:
        print(f"{status:<13} | {count}")
    cursor.execute("SELECT COUNT(*) FROM assets")
    total = cursor.fetchone()[0]
    print(f"\nTotal assets: {total}")
    conn.close()


def borrowing_summary():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Currently borrowed
    cursor.execute("SELECT COUNT(*) FROM borrowings WHERE return_date IS NULL")
    active = cursor.fetchone()[0]
    # Overdue
    cursor.execute(
        "SELECT COUNT(*) FROM borrowings WHERE return_date IS NULL AND due_date < date('now')"
    )
    overdue = cursor.fetchone()[0]
    print("\n=== Borrowing Summary ===")
    print(f"Active borrowings: {active}")
    print(f"Overdue borrowings: {overdue}")

    # Most borrowed assets
    cursor.execute(
        """SELECT a.name, COUNT(b.id) AS borrow_count
           FROM assets a
           JOIN borrowings b ON a.id = b.asset_id
           GROUP BY a.id
           ORDER BY borrow_count DESC
           LIMIT 5"""
    )
    rows = cursor.fetchall()
    print("\nTop borrowed assets:")
    if not rows:
        print("  No borrowings yet.")
    else:
        for name, cnt in rows:
            print(f"  {name} - {cnt} times")
    conn.close()


def attendance_summary():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Today's check-ins
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date(check_in) = date('now')")
    today = cursor.fetchone()[0]
    # Currently checked in
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE check_out IS NULL")
    onsite = cursor.fetchone()[0]
    print("\n=== Attendance Summary ===")
    print(f"Checked in today: {today}")
    print(f"Currently on site: {onsite}")

    # Attendance by user (last 7 days)
    cursor.execute(
        """SELECT u.username, COUNT(a.id) AS days
           FROM users u
           LEFT JOIN attendance a ON u.id = a.user_id
           WHERE date(a.check_in) >= date('now', '-7 days')
           GROUP BY u.username
           ORDER BY days DESC"""
    )
    rows = cursor.fetchall()
    print("\nAttendance last 7 days:")
    if not rows:
        print("  No data.")
    else:
        for uname, days in rows:
            print(f"  {uname}: {days} day(s)")
    conn.close()
