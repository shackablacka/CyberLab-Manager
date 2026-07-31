import subprocess
from pathlib import Path

NAME = "World-Writable Files Auditor"
DESCRIPTION = "Find world-writable files and directories, flag them for review."
ALLOWED_ROLES = ["admin", "instructor"]

SUSPICIOUS = ("/tmp", "/var/tmp", "/dev/shm", "/usr/lib", "/etc",
              "/bin", "/sbin")


def run(username, role):
    print("[*] Scanning / for world-writable files (this may take a minute)...")
    result = subprocess.run(
        ["bash", "-c",
         "find / -xdev -type f -perm -0002 ! -path '/proc/*' ! -path '/sys/*' "
         "! -path '/dev/*' 2>/dev/null"],
        capture_output=True, text=True, timeout=120,
    )
    files = result.stdout.strip().splitlines()
    print(f"[+] {len(files)} world-writable file(s) found.\n")

    for f in files[:50]:
        print(f"  {f}")
    if len(files) > 50:
        print(f"  ... and {len(files) - 50} more.")

    # Check dirs too
    result = subprocess.run(
        ["bash", "-c",
         "find / -xdev -type d -perm -0002 ! -path '/proc/*' ! -path '/sys/*' "
         "! -path '/dev/*' 2>/dev/null"],
        capture_output=True, text=True, timeout=60,
    )
    dirs = result.stdout.strip().splitlines()
    important = [d for d in dirs if any(d.startswith(s) for s in SUSPICIOUS)]
    if important:
        print("\n[!] World-writable directories in sensitive locations:")
        for d in important:
            print(f"  {d}")

    print("\n[*] Review findings. World-writable files are risky if they can be")
    print("    modified by non-trusted users.")
