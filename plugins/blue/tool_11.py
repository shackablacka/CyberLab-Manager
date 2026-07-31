import subprocess
from core.tool_runner import is_installed

NAME = "iptables Rule Auditor"
DESCRIPTION = "List iptables rules and flag permissive or missing policies."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    if not is_installed("iptables"):
        print("[!] iptables not installed.")
        return

    result = subprocess.run(["iptables", "-L", "-n", "--line-numbers"],
                            capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        print("[!] iptables failed (are you root?).")
        return

    print("--- iptables Rules ---\n")
    for line in result.stdout.splitlines():
        print(f"  {line}")

    print("\n--- Policy Summary ---\n")
    for chain in ["INPUT", "FORWARD", "OUTPUT"]:
        result = subprocess.run(["iptables", "-L", chain, "-n", "--line-numbers"],
                                capture_output=True, text=True, timeout=10)
        for line in result.stdout.splitlines():
            if "policy" in line.lower() or "target" in line.lower():
                print(f"  {chain}: {line.strip()}")

    # Check for any ACCEPT ALL inputs
    for chain in ["INPUT", "FORWARD"]:
        result = subprocess.run(["iptables", "-L", chain, "-n"],
                                capture_output=True, text=True, timeout=10)
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if "ACCEPT" in line and "0.0.0.0/0" in line and "REJECT" not in line:
                print(f"\n[!] Permissive ACCEPT rule in {chain}: {line.strip()}")
