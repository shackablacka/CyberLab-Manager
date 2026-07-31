from pathlib import Path

NAME = "User Account Auditor"
DESCRIPTION = "Audit /etc/passwd and shadow for account anomalies."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    passwd = Path("/etc/passwd").read_text().splitlines()

    print("=== Account Audit ===\n")

    # UID 0 accounts
    print("--- UID 0 accounts (should only be root) ---")
    for line in passwd:
        parts = line.split(":")
        if parts[2] == "0":
            flag = "" if parts[0] == "root" else "  <-- INVESTIGATE!"
            print(f"  {parts[0]}{flag}")

    # Login-capable shells
    print("\n--- Accounts with login shells ---")
    shells = ("/bin/bash", "/bin/sh", "/bin/zsh", "/bin/dash")
    for line in passwd:
        parts = line.split(":")
        if parts[-1].strip() in shells:
            print(f"  {parts[0]:<20} uid={parts[2]:<6} {parts[-1].strip()}")

    # Empty passwords in shadow (root only)
    print("\n--- Empty-password accounts ---")
    try:
        shadow = Path("/etc/shadow").read_text().splitlines()
        empty = [l.split(":")[0] for l in shadow if l.split(":")[1] == ""]
        if empty:
            for u in empty:
                print(f"  [!] {u} has NO PASSWORD")
        else:
            print("  [+] None found.")
    except PermissionError:
        print("  [-] /etc/shadow unreadable (need root).")

    # Locked accounts
    try:
        locked = sum(1 for l in shadow if l.split(":")[1].startswith("!"))
        print(f"\n[*] Locked accounts: {locked}")
    except (PermissionError, NameError):
        pass
