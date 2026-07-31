import random
import subprocess
from core.tool_runner import run_tool, is_installed

NAME = "MAC Address Changer"
DESCRIPTION = "Change a lab interface MAC address (macchanger)."
ALLOWED_ROLES = ["admin", "instructor"]


def random_mac():
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ":".join(f"{b:02x}" for b in mac)


def run(username, role):
    iface = input("Interface (e.g. eth0): ").strip()
    if not iface:
        return

    print("1. Show current MAC")
    print("2. Set random MAC")
    print("3. Set specific MAC")
    choice = input("Select: ").strip()

    if choice == "1":
        subprocess.run(["ip", "link", "show", iface], check=False)
    elif choice == "2":
        mac = random_mac()
        apply_mac(iface, mac)
    elif choice == "3":
        mac = input("New MAC (e.g. 00:16:3e:xx:xx:xx): ").strip()
        if mac.count(":") != 5:
            print("[!] Invalid MAC format.")
            return
        apply_mac(iface, mac)
    else:
        print("[!] Invalid choice.")


def apply_mac(iface, mac):
    print(f"[*] Setting {iface} MAC to {mac}...")
    subprocess.run(["ip", "link", "set", "dev", iface, "down"], check=False)
    result = subprocess.run(
        ["ip", "link", "set", "dev", iface, "address", mac], check=False
    )
    subprocess.run(["ip", "link", "set", "dev", iface, "up"], check=False)

    if result.returncode == 0:
        print(f"[+] MAC changed. Verify with: ip link show {iface}")
        print("[!] Note: changes revert on reboot.")
    else:
        print("[!] Failed — is the interface up/managed by NetworkManager?")
