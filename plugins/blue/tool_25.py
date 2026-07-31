import subprocess
from pathlib import Path

NAME = "Recent User Activity"
DESCRIPTION = "Summarize recent logins and sudo usage."
ALLOWED_ROLES = ["admin", "instructor", "student"]

AUTH_LOG = Path("/var/log/auth.log")


def run(username, role):
    print("=== Recent User Activity ===\n")

    # last logins
    last = subprocess.run(["last", "-a", "-n", "15"], capture_output=True,
                          text=True, timeout=10)
    print("--- Recently logged in users ---")
    print(last.stdout if last.returncode == 0 else "(last not available)")

    # failed logins
    if AUTH_LOG.exists():
        try:
            content = AUTH_LOG.read_text(errors="ignore")
            failed = [l for l in content.splitlines() if "Failed password" in l]
            print(f"\n--- Failed attempts (last 24h if available) ---")
            for line in failed[-5:]:
                print(f"  {line[:130]}")
            print(f"\n[+] Total failed attempts in log: {len(failed)}")
        except PermissionError:
            print("\n[!] Cannot read auth.log (need root).")
