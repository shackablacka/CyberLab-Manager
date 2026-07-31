import subprocess
from collections import Counter

NAME = "Process Auditor"
DESCRIPTION = "List processes and flag suspicious indicators."
ALLOWED_ROLES = ["admin", "instructor", "student"]

SUSPICIOUS_PATHS = ("/tmp/", "/dev/shm/", "/var/tmp/", "/run/user/")
SUSPICIOUS_NAMES = ("nc", "ncat", "netcat", "socat", "miner", "xmrig")


def run(username, role):
    result = subprocess.run(["ps", "aux"], capture_output=True,
                            text=True, timeout=10)
    lines = result.stdout.splitlines()
    print(f"[*] {len(lines) - 1} processes running.\n")

    # Top CPU consumers
    print("--- Top 5 by CPU ---")
    rows = []
    for line in lines[1:]:
        parts = line.split(None, 10)
        if len(parts) == 11:
            rows.append((float(parts[2]), parts[0], parts[1], parts[10]))
    for cpu, user, pid, cmd in sorted(rows, reverse=True)[:5]:
        print(f"  {cpu:>5.1f}%  {user:<10} PID {pid:<8} {cmd[:60]}")

    # Suspicious indicators
    print("\n--- Suspicious Indicators ---")
    findings = 0
    for line in lines[1:]:
        low = line.lower()
        if any(p in low for p in SUSPICIOUS_PATHS):
            print(f"  [!] Temp-dir execution: {line[:100]}")
            findings += 1
        parts = line.split(None, 10)
        if len(parts) == 11:
            name = parts[10].rsplit("/", 1)[-1].lower()
            if name in SUSPICIOUS_NAMES:
                print(f"  [!] Flagged binary '{name}': PID {parts[1]} ({parts[0]})")
                findings += 1

    if findings == 0:
        print("  [+] No obvious indicators found.")

    # Per-user counts
    print("\n--- Processes per user ---")
    counts = Counter(line.split(None, 1)[0] for line in lines[1:])
    for user, count in counts.most_common(8):
        print(f"  {user:<12} {count:>4}")
