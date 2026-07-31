import subprocess
from pathlib import Path

NAME = "Cron Job Auditor"
DESCRIPTION = "List cron jobs from system/user crontabs and flag suspicious entries."
ALLOWED_ROLES = ["admin", "instructor", "student"]

SUSPICIOUS = ("/tmp/", "/var/tmp/", "wget", "curl", "nc", "bash -i",
              "python -c", "base64", "chmod")


def run(username, role):
    print("=== Cron Jobs ===")
    
    # System crontab
    for path in [Path("/etc/crontab"), *Path("/etc/cron.d").glob("*")]:
        if path.is_file():
            print(f"\n--- {path} ---")
            for line in path.read_text(errors="ignore").splitlines():
                if line and not line.startswith("#"):
                    print(f"  {line}")

    # Per-hourly/daily/weekly
    for sub in ["/etc/cron.hourly", "/etc/cron.daily", "/etc/cron.weekly",
                "/etc/cron.monthly"]:
        dir_path = Path(sub)
        if dir_path.is_dir():
            scripts = [p for p in dir_path.iterdir() if p.is_file()]
            if scripts:
                print(f"\n--- {sub} ---")
                for p in scripts:
                    print(f"  {p.name}")

    # User crontabs
    crontabs = subprocess.run(["ls", "/var/spool/cron/crontabs"],
                              capture_output=True, text=True)
    if crontabs.stdout:
        print("\n--- User crontabs ---")
        for user in crontabs.stdout.split():
            print(f"\n  [{user}]")
            result = subprocess.run(["crontab", "-u", user, "-l"],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if line and not line.startswith("#"):
                        print(f"    {line}")

    # Scan all cron outputs for suspicious commands
    print("\n--- Suspicious Indicators ---")
    all_cron = subprocess.run(
        ["bash", "-c", "cat /etc/crontab /etc/cron.d/* 2>/dev/null"],
        capture_output=True, text=True, timeout=5).stdout
    for keyword in SUSPICIOUS:
        if keyword in all_cron:
            print(f"  [!] Found suspicious string: {keyword}")

    # Check cron service
    result = subprocess.run(["systemctl", "is-active", "cron"],
                            capture_output=True, text=True)
    print(f"\n[*] Cron service: {result.stdout.strip()}")
