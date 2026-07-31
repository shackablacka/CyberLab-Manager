from collections import Counter
from pathlib import Path
import re

NAME = "Failed Login Analyzer"
DESCRIPTION = "Parse auth logs for failed logins and brute-force patterns."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/blue/reports")
LOG_PATHS = [Path("/var/log/auth.log"), Path("/var/log/secure")]


def run(username, role):
    log_path = next((p for p in LOG_PATHS if p.exists()), None)
    if not log_path:
        print("[!] No auth log found (/var/log/auth.log).")
        return

    try:
        content = log_path.read_text(errors="ignore")
    except PermissionError:
        print("[!] Permission denied — run as root.")
        return

    failed_ips, failed_users = Counter(), Counter()
    for line in content.splitlines():
        if "Failed password" in line:
            ip = re.search(r"from (\d+\.\d+\.\d+\.\d+)", line)
            user = re.search(r"for (?:invalid user )?(\S+) from", line)
            if ip:
                failed_ips[ip.group(1)] += 1
            if user:
                failed_users[user.group(1)] += 1

    print(f"\n[*] Analyzed {log_path}")
    print(f"[+] Total failed attempts: {sum(failed_ips.values())}")

    print("\n--- Top attacking IPs ---")
    for ip, count in failed_ips.most_common(10):
        flag = "  <-- BRUTE FORCE?" if count >= 10 else ""
        print(f"  {ip:<18} {count:>5} attempts{flag}")

    print("\n--- Top targeted usernames ---")
    for user, count in failed_users.most_common(10):
        print(f"  {user:<18} {count:>5} attempts")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / "failed_logins.txt"
    out.write_text(
        "Top IPs:\n" + "\n".join(f"{ip} {c}" for ip, c in failed_ips.most_common())
        + "\n\nTop users:\n"
        + "\n".join(f"{u} {c}" for u, c in failed_users.most_common()),
        encoding="utf-8",
    )
    print(f"\n[+] Report saved: {out}")
