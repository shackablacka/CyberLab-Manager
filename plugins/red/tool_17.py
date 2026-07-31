import subprocess
from core.tool_runner import run_tool, is_installed

NAME = "ARP Network Scanner"
DESCRIPTION = "Discover live hosts on the local LAN."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    iface = input("Interface (default eth0): ").strip() or "eth0"

    if is_installed("arp-scan"):
        run_tool("arp-scan", ["-I", iface, "--localnet"], package="arp-scan")
        return

    print("[*] arp-scan not installed; showing current ARP/neighbor table.")
    print("    (Run the Ping Sweep tool first to populate it.)\n")
    subprocess.run(["ip", "neigh", "show"], check=False)
