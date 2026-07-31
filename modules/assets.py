import sqlite3
import logging

from core.auth import DATABASE

log = logging.getLogger("cyberlab.modules.assets")

def run(username: str, role: str):
    while True:
        print("\n=== Asset Management ===")
        print("1. List Assets")
        print("2. Add Asset")
        print("3. Update Asset")
        print("4. Remove Asset")
        print("0. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            list_assets()
        elif choice == "2":
            add_asset()
        elif choice == "3":
            update_asset()
        elif choice == "4":
            remove_asset()
        else:
            print("[!] Invalid option.")


def get_assets():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, serial_number, location, status FROM assets ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows


def list_assets():
    assets = get_assets()
    if not assets:
        print("\nNo assets found.")
        return
    print("\nID | Name | Category | Serial No | Location | Status")
    print("-" * 70)
    for aid, name, cat, serial, loc, status in assets:
        print(f"{aid} | {name} | {cat} | {serial or '-'} | {loc or '-'} | {status}")


def add_asset():
    name = input("Asset name: ").strip()
    if not name:
        print("[!] Name required.")
        return
    category = input("Category: ").strip()
    serial = input("Serial number: ").strip()
    location = input("Location: ").strip()
    status = input("Status (available/borrowed/maintenance): ").strip().lower()
    if status not in ("available", "borrowed", "maintenance"):
        print("[!] Invalid status.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO assets(name, category, serial_number, location, status) VALUES (?, ?, ?, ?, ?)",
            (name, category, serial or None, location or None, status),
        )
        conn.commit()
        print(f"[+] Asset '{name}' added.")
    except sqlite3.IntegrityError:
        print("[!] Serial number already exists.")
    conn.close()


def update_asset():
    asset_id = input("Asset ID to update: ").strip()
    if not asset_id.isdigit():
        print("[!] Invalid ID.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assets WHERE id=?", (int(asset_id),))
    asset = cursor.fetchone()
    if not asset:
        print("[!] Asset not found.")
        conn.close()
        return

    print("\nLeave blank to keep current value.")
    name = input(f"Name ({asset[1]}): ").strip() or asset[1]
    category = input(f"Category ({asset[2]}): ").strip() or asset[2]
    serial = input(f"Serial ({asset[3]}): ").strip() or asset[3]
    location = input(f"Location ({asset[4]}): ").strip() or asset[4]
    status = input(f"Status ({asset[5]}): ").strip().lower() or asset[5]
    if status not in ("available", "borrowed", "maintenance"):
        print("[!] Invalid status.")
        conn.close()
        return

    cursor.execute(
        """UPDATE assets SET name=?, category=?, serial_number=?, location=?, status=? WHERE id=?""",
        (name, category, serial, location, status, int(asset_id)),
    )
    conn.commit()
    print("[+] Asset updated.")
    conn.close()


def remove_asset():
    asset_id = input("Asset ID to remove: ").strip()
    if not asset_id.isdigit():
        print("[!] Invalid ID.")
        return

    confirm = input("Are you sure? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("[!] Cancelled.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assets WHERE id=?", (int(asset_id),))
    conn.commit()
    if cursor.rowcount == 0:
        print("[!] Asset not found.")
    else:
        print("[+] Asset removed.")
    conn.close()
