import shutil
import subprocess

NAME = "Auditd Status Checker"
DESCRIPTION = "Review Linux auditd status and loaded audit rules."
ALLOWED_ROLES = ["admin", "instructor"]

def run(username, role):
    if not shutil.which("auditctl"):
        print("[!] auditctl is not installed.")
        print("[*] Install with: apt install auditd")
        return

    print("=== Auditd Service Status ===")
    service = subprocess.run(
        ["systemctl", "is-active", "auditd"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    print(f"  Service: {service.stdout.strip() or 'unknown'}")

    print("\n=== Kernel Audit Status ===")
    status = subprocess.run(
        ["auditctl", "-s"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    print(status.stdout or status.stderr or "(no output)")

    print("\n=== Loaded Audit Rules ===")
    rules = subprocess.run(
        ["auditctl", "-l"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    print(rules.stdout or rules.stderr or "(no rules or permission denied)")

    if rules.returncode != 0:
        print("\n[!] Rule listing returned a non-zero status.")
        print("[*] Run as root and verify auditd is active.")
