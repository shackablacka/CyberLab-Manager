"""Role-aware CyberLab-Manager dashboard."""

import logging

from modules import (
    assets,
    attendance,
    blueteam,
    borrowing,
    reports,
    redteam,
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
    ("Lab Setup", setup.run, ["admin"]),
]


def run_dashboard(username: str, role: str) -> None:
    while True:
        print("\n=== CyberLab-Manager Dashboard ===")
        print(f"User: {username} | Role: {role}\n")

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
            print("[!] Module failed. Check the log for details.")
