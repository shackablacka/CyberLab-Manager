"""Role-aware CyberLab-Manager dashboard."""

import logging
import shutil
from datetime import datetime
from pathlib import Path

from core.loader import load_plugins
from modules import (
    assets,
    attendance,
    blueteam,
    borrowing,
    catalog,
    purpleteam,
    redteam,
    reports,
    setup,
    users,
)

log = logging.getLogger("cyberlab.menu")

MENU_ITEMS = [
    ("User Management", users.run, ["admin"]),
    ("Assets", assets.run, ["admin", "student", "instructor"]),
    ("Attendance", attendance.run, ["admin", "student", "instructor"]),
    ("Borrowing", borrowing.run, ["admin", "student", "instructor"]),
    ("Reports", reports.run, ["admin"]),
    ("Red Team Tools", redteam.run, ["admin", "instructor"]),
    ("Blue Team Tools", blueteam.run, ["admin", "instructor", "student"]),
    ("Purple Team Exercises", purpleteam.run, ["admin", "instructor"]),
    ("Tool Catalog", catalog.run, ["admin", "instructor", "student"]),
    ("Lab Setup", setup.run, ["admin"]),
]


def _plugin_counts(role: str) -> tuple[int, int]:
    red = sum(1 for p in load_plugins("red").values() if role in p["allowed_roles"])
    blue = sum(1 for p in load_plugins("blue").values() if role in p["allowed_roles"])
    return red, blue


def _print_banner(username: str, role: str) -> None:
    now = datetime.now()
    red_count, blue_count = _plugin_counts(role)
    db_ok = Path("database/database.db").exists()
    disk = shutil.disk_usage(".")
    free_gb = disk.free / (1024 ** 3)

    print("\n" + "=" * 58)
    print("  CyberLab-Manager")
    print("  Red / Blue / Purple laboratory control center")
    print("=" * 58)
    print(f"  User : {username}")
    print(f"  Role : {role}")
    print(f"  Time : {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Tools: {red_count} red  |  {blue_count} blue")
    print(f"  DB   : {'ready' if db_ok else 'missing'}")
    print(f"  Disk : {free_gb:.1f} GB free")

    if now.year >= 2026:
        print("  [!] System clock looks wrong. Run: timedatectl set-ntp true")
    print("=" * 58)


def run_dashboard(username: str, role: str) -> None:
    while True:
        _print_banner(username, role)
        print()

        available = [
            (title, function)
            for title, function, allowed_roles in MENU_ITEMS
            if role in allowed_roles
        ]

        for number, (title, _) in enumerate(available, start=1):
            print(f"{number}. {title}")
        print("0. Logout")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            log.info("User logged out: %s", username)
            print("Logging out...")
            return

        if not choice.isdigit():
            print("[!] Please enter a number.")
            continue

        index = int(choice) - 1
        if not 0 <= index < len(available):
            print("[!] Invalid option.")
            continue

        title, function = available[index]
        log.info("User %s opened module: %s", username, title)

        try:
            function(username, role)
        except Exception:
            log.exception("Module failed: %s", title)
            print("[!] Module failed. Check logs/cyberlab.log.")
