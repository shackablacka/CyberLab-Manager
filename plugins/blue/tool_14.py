import subprocess
from core.tool_runner import is_installed

NAME = "Fail2Ban Manager"
DESCRIPTION = "Check fail2ban jails and banned IPs."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    if not is_installed("fail2ban-client"):
        print("[!] fail2ban-client not installed.")
        return

    # Overall status
    result = subprocess.run(["fail2ban-client", "status"], capture_output=True,
                            text=True, timeout=10)
    if result.returncode != 0:
        print("[!] fail2ban-client failed (is fail2ban running?).")
        return
    print("--- Fail2Ban Status ---")
    print(result.stdout)

    # List jails
    jail_list = subprocess.run(["fail2ban-client", "status"], capture_output=True,
                               text=True, timeout=10).stdout
    lines = jail_list.splitlines()
    jails = []
    for line in lines:
        if "Jail list:" in line:
            jails = line.split("Jail list:")[1].strip().split(", ")
            break

    if not jails:
        print("[*] No active jails.")
        return

    for jail in jails:
        status = subprocess.run(["fail2ban-client", "status", jail],
                                capture_output=True, text=True, timeout=10)
        print(f"\n--- {jail} ---")
        if status.returncode == 0:
            print(status.stdout)
        else:
            print("  (cannot retrieve status)")
