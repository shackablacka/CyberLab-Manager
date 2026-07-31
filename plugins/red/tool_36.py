import subprocess
from core.tool_runner import is_installed, run_tool

NAME = "Wireless Audit Helper"
DESCRIPTION = "Show wireless interfaces and toggle monitor mode."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("1. List wireless interfaces")
    print("2. Enable monitor mode (airmon-ng)")
    print("3. Disable monitor mode")
    choice = input("Select: ").strip()

    if choice == "1":
        if is_installed("iwconfig"):
            subprocess.run(["iwconfig"], check=False)
        else:
            subprocess.run(["iw", "dev"], check=False)
    elif choice == "2":
        iface = input("Interface (e.g. wlan0): ").strip()
        if iface:
            run_tool("airmon-ng", ["start", iface], package="aircrack-ng")
    elif choice == "3":
        iface = input("Monitor interface (e.g. wlan0mon): ").strip()
        if iface:
            run_tool("airmon-ng", ["stop", iface], package="aircrack-ng")
    else:
        print("[!] Invalid choice.")
