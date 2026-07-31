from collections import Counter
from pathlib import Path

NAME = "Sudo Usage Reviewer"
DESCRIPTION = "Summarize sudo command usage from auth logs."
ALLOWED_ROLES = ["admin", "instructor"]

LOG_PATHS = [Path("/var/log/auth.log"), Path("/var/log/secure")]


def run(username, role):
    log_path = next((p for p in LOG_PATHS if p.exists()), None)
    if not log_path:
        print("[!] No auth log found.")
        return

    try:
        lines = log_path.read_text(errors="ignore").splitlines()
    except PermissionError:
        print("[!] Permission denied — run as root.")
        return

    users, commands, failures = Counter(), Counter(), []
    for line in lines:
        if "COMMAND=" in line:
            user = line.split()[1] if len(line.split()) > 1 else "?"
            cmd = line.split("COMMAND=", 1)[1].strip()
            users[user] += 1
            commands[cmd.split()[0] if cmd else "?"] += 1
        if "authentication failure" in line and "sudo" in line:
            failures.append(line)

    print("=== Sudo Activity ===\n")
    print("--- By user ---")
    for user, count in users.most_common(10):
        print(f"  {user:<15} {count:>4} command(s)")

    print("\n--- Most-run commands ---")
    for cmd, count in commands.most_common(10):
        print(f"  {cmd:<25} {count:>4}x")

    print(f"\n[*] Sudo auth failures: {len(failures)}")
    for line in failures[-5:]:
        print(f"  [!] {line[:130]}")
