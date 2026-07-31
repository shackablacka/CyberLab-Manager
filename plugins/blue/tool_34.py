import json
import re
from collections import Counter
from pathlib import Path

NAME = "Log Anomaly Detector"
DESCRIPTION = "Detect repeated authentication and privilege-related events."
ALLOWED_ROLES = ["admin", "instructor", "student"]

REPORT_DIR = Path("tools/blue/reports")
LOG_PATHS = [
    Path("/var/log/auth.log"),
    Path("/var/log/secure"),
    Path("/var/log/syslog"),
]

PATTERNS = {
    "failed_password": "Failed password",
    "invalid_user": "Invalid user",
    "sudo_failure": "authentication failure",
    "accepted_login": "Accepted ",
    "session_opened": "session opened",
}


def run(username, role):
    available = [path for path in LOG_PATHS if path.exists()]

    if not available:
        print("[!] No supported log file found.")
        print("[*] Checked: " + ", ".join(str(path) for path in LOG_PATHS))
        return

    print("Available logs:")
    for index, path in enumerate(available, 1):
        print(f"  {index}. {path}")

    choice = input("Select log [1]: ").strip()
    index = int(choice) - 1 if choice.isdigit() else 0

    if not 0 <= index < len(available):
        print("[!] Invalid selection.")
        return

    path = available[index]

    try:
        lines = path.read_text(errors="ignore").splitlines()
    except PermissionError:
        print("[!] Permission denied. Run as root.")
        return

    counts = Counter()
    source_ips = Counter()

    for line in lines:
        for name, marker in PATTERNS.items():
            if marker.lower() in line.lower():
                counts[name] += 1

        match = re.search(r"\b(?:from|rhost=)(\d{1,3}(?:\.\d{1,3}){3})", line)
        if match and "failed" in line.lower():
            source_ips[match.group(1)] += 1

    print(f"\n[*] Analyzed {len(lines)} lines from {path}")

    print("\n--- Event counts ---")
    for name, count in counts.items():
        print(f"  {name:<20} {count}")

    print("\n--- Repeated failed-login sources ---")
    repeated = [(ip, count) for ip, count in source_ips.items() if count >= 5]

    if not repeated:
        print("  No repeated source exceeded the threshold.")
    else:
        for ip, count in sorted(repeated, key=lambda item: item[1], reverse=True):
            print(f"  [!] {ip:<18} {count} failed attempts")

    report = {
        "log": str(path),
        "line_count": len(lines),
        "event_counts": dict(counts),
        "failed_source_ips": dict(source_ips),
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORT_DIR / "log_anomaly_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n[+] Report saved to {output}")
