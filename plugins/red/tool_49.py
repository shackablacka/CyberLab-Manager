import subprocess
from core.tool_runner import run_tool, is_installed

NAME = "DNS Zone Transfer Tester"
DESCRIPTION = "Attempt AXFR zone transfer against a lab DNS server."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    domain = input("Target domain (lab only): ").strip()
    if not domain:
        return

    if not is_installed("dig"):
        print("[!] 'dig' is not installed.")
        run_tool("dig", [], package="dnsutils")
        return

    print(f"[*] Finding nameservers for {domain}...")
    result = subprocess.run(
        ["dig", "+short", "NS", domain],
        capture_output=True, text=True, timeout=10,
    )
    nameservers = [ns.rstrip(".") for ns in result.stdout.split()]

    if not nameservers:
        print("[!] No nameservers found.")
        return

    print(f"[+] Found {len(nameservers)} nameserver(s). Attempting AXFR...\n")
    for ns in nameservers:
        print(f"--- @{ns} ---")
        result = subprocess.run(
            ["dig", f"@{ns}", domain, "AXFR"],
            capture_output=True, text=True, timeout=15,
        )
        out = result.stdout
        if "Transfer failed" in out or "failed" in out.lower():
            print("  [+] Transfer refused (correctly configured).")
        elif "XFR size" in out:
            print("  [!] ZONE TRANSFER SUCCEEDED — misconfiguration!")
            print(out[:2000])
        else:
            print(f"  [~] Unexpected response:\n{out[:400]}")
