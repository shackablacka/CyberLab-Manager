import shutil
import subprocess
from pathlib import Path

NAME = "AppArmor / SELinux Checker"
DESCRIPTION = "Check mandatory access control framework status."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    found = False

    # AppArmor
    if shutil.which("aa-status"):
        found = True
        print("=== AppArmor Status ===\n")
        result = subprocess.run(
            ["aa-status"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr or "[!] aa-status failed (run as root).")

        # Check for unconfined processes
        if "unconfined" in (result.stdout or "").lower():
            print("[!] Some processes are running UNCONFINED.")

    elif Path("/sys/module/apparmor").exists():
        found = True
        print("[i] AppArmor kernel module loaded but aa-status not available.")
        print("[*] Install with: apt install apparmor-utils")

    # SELinux
    if shutil.which("sestatus"):
        found = True
        print("=== SELinux Status ===\n")
        result = subprocess.run(
            ["sestatus"],
            capture_output=True, text=True, timeout=10,
        )
        print(result.stdout or result.stderr)

        if "disabled" in (result.stdout or "").lower():
            print("[!] SELinux is DISABLED.")
        elif "permissive" in (result.stdout or "").lower():
            print("[!] SELinux is in PERMISSIVE mode (not enforcing).")

    elif shutil.which("getenforce"):
        found = True
        result = subprocess.run(
            ["getenforce"],
            capture_output=True, text=True, timeout=5,
        )
        print(f"SELinux mode: {result.stdout.strip()}")

    if not found:
        print("[!] Neither AppArmor nor SELinux detected.")
        print("[*] Consider enabling a MAC framework for defense in depth.")
