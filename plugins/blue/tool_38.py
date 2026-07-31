import json
import os
import time
from pathlib import Path

NAME = "Disk Usage Anomaly Auditor"
DESCRIPTION = "Find unusually large or recently changed files."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/blue/reports")


def run(username, role):
    raw_path = input("Directory to scan (default /var/log): ").strip()
    directory = Path(raw_path or "/var/log")

    if not directory.is_dir():
        print("[!] Directory does not exist.")
        return

    raw_size = input("Large-file threshold MB (default 50): ").strip()
    threshold_mb = float(raw_size) if raw_size else 50.0

    raw_hours = input("Recent-file window hours (default 24): ").strip()
    recent_hours = float(raw_hours) if raw_hours else 24.0

    threshold = threshold_mb * 1024 * 1024
    cutoff = time.time() - (recent_hours * 3600)

    large_files = []
    recent_files = []
    scanned = 0

    for root, dirs, files in os.walk(directory, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]

        for filename in files:
            path = Path(root) / filename

            try:
                info = path.stat()
            except OSError:
                continue

            scanned += 1

            if info.st_size >= threshold:
                large_files.append((info.st_size, path))

            if info.st_mtime >= cutoff:
                recent_files.append((info.st_mtime, path))

            if scanned >= 100000:
                print("[!] Scan limit reached at 100,000 files.")
                break

        if scanned >= 100000:
            break

    large_files.sort(reverse=True, key=lambda item: item[0])
    recent_files.sort(reverse=True, key=lambda item: item[0])

    print(f"\n[*] Scanned approximately {scanned} file(s).")

    print("\n--- Largest files ---")
    if not large_files:
        print("  None exceeded the threshold.")
    else:
        for size, path in large_files[:20]:
            print(f"  {size / 1024 / 1024:8.1f} MB  {path}")

    print(f"\n--- Files changed in the last {recent_hours:g} hour(s) ---")
    if not recent_files:
        print("  None found.")
    else:
        for mtime, path in recent_files[:20]:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
            print(f"  {stamp}  {path}")

    report = {
        "directory": str(directory),
        "scanned": scanned,
        "large_files": [
            {"path": str(path), "bytes": size}
            for size, path in large_files[:100]
        ],
        "recent_files": [
            {"path": str(path), "mtime": mtime}
            for mtime, path in recent_files[:100]
        ],
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORT_DIR / "disk_usage_report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n[+] Report saved to {output}")
