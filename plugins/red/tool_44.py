import ftplib
import time
from pathlib import Path

NAME = "Password Spray Auditor"
DESCRIPTION = "Spray ONE password across many lab FTP accounts."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("[!] LAB USE ONLY — password spraying locks accounts in real")
    print("    environments. Confirm your target is an authorized lab.")
    confirm = input("Type 'LAB' to confirm: ").strip()
    if confirm != "LAB":
        print("[!] Aborted.")
        return

    target = input("Target FTP IP: ").strip()
    user_file = input("Username list file: ").strip()
    password = input("Single password to spray: ")

    if not target or not password or not Path(user_file).is_file():
        print("[!] Target, password, and a valid user list are required.")
        return

    users = [u.strip() for u in Path(user_file).read_text().splitlines() if u.strip()]
    print(f"[*] Spraying '{password}' across {len(users)} account(s) on {target}...")
    print("[*] 1.5s delay between attempts to avoid lockouts.\n")

    hits = []
    for user in users:
        try:
            ftp = ftplib.FTP()
            ftp.connect(target, 21, timeout=5)
            ftp.login(user, password)
            print(f"  [!] VALID: {user}:{password}")
            hits.append(f"{user}:{password}")
            ftp.quit()
        except ftplib.error_perm:
            print(f"  [-] failed: {user}")
        except OSError as e:
            print(f"  [!] Connection error: {e}")
            break
        time.sleep(1.5)

    print(f"\n[+] Spray complete. {len(hits)} valid credential(s) found.")
