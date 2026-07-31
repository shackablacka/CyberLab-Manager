import subprocess
from core.tool_runner import is_installed

NAME = "UFW Status Auditor"
DESCRIPTION = "Check UFW firewall status and rules."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    if not is_installed("ufw"):
        print("[!] ufw not installed.")
        return

    result = subprocess.run(["ufw", "status", "verbose"], capture_output=True,
                            text=True, timeout=10)
    print("--- UFW Status ---")
    print(result.stdout or "(no output)")

    result = subprocess.run(["ufw", "status", "numbered"], capture_output=True,
                            text=True, timeout=10)
    print("\n--- UFW Rules (numbered) ---")
    print(result.stdout or "(no rules)")

    # Check default policy
    result = subprocess.run(["ufw", "show", "raw"], capture_output=True,
                            text=True, timeout=10)
    if result.stdout:
        print("\n--- Raw ufw rules ---")
        print(result.stdout[:2000])
