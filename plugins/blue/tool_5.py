from pathlib import Path

NAME = "Auth Log Searcher"
DESCRIPTION = "Search auth logs by keyword with context."
ALLOWED_ROLES = ["admin", "instructor"]

LOG_PATHS = [Path("/var/log/auth.log"), Path("/var/log/secure")]


def run(username, role):
    log_path = next((p for p in LOG_PATHS if p.exists()), None)
    if not log_path:
        print("[!] No auth log found.")
        return

    keyword = input("Search keyword (e.g. 'sudo', IP, username): ").strip()
    if not keyword:
        return

    try:
        lines = log_path.read_text(errors="ignore").splitlines()
    except PermissionError:
        print("[!] Permission denied — run as root.")
        return

    matches = [(i, l) for i, l in enumerate(lines) if keyword.lower() in l.lower()]
    print(f"\n[+] {len(matches)} match(es) in {log_path}")

    if not matches:
        return

    show = input("How many to display (default 15, newest last): ").strip()
    show = int(show) if show.isdigit() else 15

    for _, line in matches[-show:]:
        print(f"  {line[:160]}")

    if len(matches) > show:
        print(f"\n  ... {len(matches) - show} earlier match(es) hidden.")
