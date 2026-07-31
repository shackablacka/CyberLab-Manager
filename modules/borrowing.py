import sqlite3
import logging
from datetime import datetime, timedelta

from core.auth import DATABASE

log = logging.getLogger("cyberlab.modules.borrowing")

def run(username: str, role: str):
    while True:
        print("\n=== Borrowing ===")
        print("1. Borrow Asset")
        print("2. Return Asset")
        print("3. View Active Borrowings")
        print("4. View Borrowing History")
        print("0. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            borrow_asset(username)
        elif choice == "2":
            return_asset(username)
        elif choice == "3":
            view_active(role)
        elif choice == "4":
            view_history(role)
        else:
            print("[!] Invalid option.")


def get_user_id(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def borrow_asset(username):
    user_id = get_user_id(username)
    if not user_id:
        print("[!] User not found.")
        return

    asset_id = input("Asset ID to borrow: ").strip()
    if not asset_id.isdigit():
        print("[!] Invalid asset ID.")
        return

    days = input("Borrow duration (days, default 7): ").strip()
    try:
        days = int(days) if days else 7
    except ValueError:
        print("[!] Invalid day count.")
        return
    due_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check asset exists and available
    cursor.execute("SELECT name, status FROM assets WHERE id=?", (int(asset_id),))
    asset = cursor.fetchone()
    if not asset:
        print("[!] Asset not found.")
        conn.close()
        return
    if asset[1] != "available":
        print(f"[!] Asset '{asset[0]}' is not available (status: {asset[1]}).")
        conn.close()
        return

    # Create borrowing record
    cursor.execute(
        "INSERT INTO borrowings(user_id, asset_id, due_date) VALUES (?, ?, ?)",
        (user_id, int(asset_id), due_date),
    )
    # Update asset status
    cursor.execute(
        "UPDATE assets SET status='borrowed' WHERE id=?",
        (int(asset_id),),
    )
    conn.commit()
    conn.close()
    print(f"[+] You borrowed '{asset[0]}'. Due date: {due_date}")


def return_asset(username):
    user_id = get_user_id(username)
    if not user_id:
        print("[!] User not found.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Find active borrowings for this user
    cursor.execute(
        """SELECT b.id, a.name, a.id AS asset_id
           FROM borrowings b
           JOIN assets a ON b.asset_id = a.id
           WHERE b.user_id=? AND b.return_date IS NULL
           ORDER BY b.borrow_date""",
        (user_id,),
    )
    active = cursor.fetchall()

    if not active:
        print("[!] You have no active borrowings.")
        conn.close()
        return

    print("\nActive borrowings:")
    for bid, name, aid in active:
        print(f"  Borrowing ID {bid}: {name} (Asset {aid})")

    b_id = input("Enter Borrowing ID to return: ").strip()
    if not b_id.isdigit():
        print("[!] Invalid ID.")
        conn.close()
        return

    # Verify it's one of this user's active borrowings
    if not any(int(b_id) == r[0] for r in active):
        print("[!] That borrowing ID is not yours.")
        conn.close()
        return

    cursor.execute(
        "UPDATE borrowings SET return_date=? WHERE id=?",
        (datetime.now().isoformat(), int(b_id)),
    )
    cursor.execute(
        """UPDATE assets SET status='available'
           WHERE id=(SELECT asset_id FROM borrowings WHERE id=?)""",
        (int(b_id),),
    )
    conn.commit()
    conn.close()
    print("[+] Asset returned.")


def view_active(role):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if role == "admin":
        cursor.execute(
            """SELECT b.id, u.username, a.name, b.borrow_date, b.due_date
               FROM borrowings b
               JOIN users u ON b.user_id = u.id
               JOIN assets a ON b.asset_id = a.id
               WHERE b.return_date IS NULL
               ORDER BY b.due_date"""
        )
    else:
        user_id = get_user_id(input("Enter username (or your own if blank): ").strip() or "self")
        if not user_id:
            print("[!] User not found.")
            conn.close()
            return
        cursor.execute(
            """SELECT b.id, u.username, a.name, b.borrow_date, b.due_date
               FROM borrowings b
               JOIN users u ON b.user_id = u.id
               JOIN assets a ON b.asset_id = a.id
               WHERE b.user_id=? AND b.return_date IS NULL
               ORDER BY b.due_date""",
            (user_id,),
        )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("\nNo active borrowings.")
        return
    print("\nID | User | Asset | Borrow Date | Due Date")
    print("-" * 60)
    for bid, uname, aname, bdate, due in rows:
        print(f"{bid} | {uname} | {aname} | {bdate[:10]} | {due}")


def view_history(role):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if role == "admin":
        cursor.execute(
            """SELECT b.id, u.username, a.name, b.borrow_date, b.due_date, b.return_date
               FROM borrowings b
               JOIN users u ON b.user_id = u.id
               JOIN assets a ON b.asset_id = a.id
               ORDER BY b.borrow_date DESC"""
        )
    else:
        user_id = get_user_id(input("Enter username (or your own if blank): ").strip() or "self")
        if not user_id:
            print("[!] User not found.")
            conn.close()
            return
        cursor.execute(
            """SELECT b.id, u.username, a.name, b.borrow_date, b.due_date, b.return_date
               FROM borrowings b
               JOIN users u ON b.user_id = u.id
               JOIN assets a ON b.asset_id = a.id
               WHERE b.user_id=?
               ORDER BY b.borrow_date DESC""",
            (user_id,),
        )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("\nNo history found.")
        return
    print("\nID | User | Asset | Borrow Date | Due Date | Return Date")
    print("-" * 75)
    for bid, uname, aname, bdate, due, ret in rows:
        ret = ret[:10] if ret else "not returned"
        print(f"{bid} | {uname} | {aname} | {bdate[:10]} | {due} | {ret}")
