import shutil
import subprocess
from pathlib import Path

NAME = "Kernel Module Auditor"
DESCRIPTION = "List loaded kernel modules and flag suspicious indicators."
ALLOWED_ROLES = ["admin", "instructor"]

SUSPICIOUS_NAMES = {
    "diamorphine",
    "reptile",
    "adore",
    "suterusu",
    "kbeast",
    "rootkit",
    "hide",
}


def run(username, role):
    if shutil.which("lsmod"):
        result = subprocess.run(
            ["lsmod"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = result.stdout.splitlines()[1:]
        modules = [line.split()[0] for line in lines if line.split()]
    else:
        try:
            lines = Path("/proc/modules").read_text().splitlines()
            modules = [line.split()[0] for line in lines if line.split()]
        except OSError:
            print("[!] Could not read loaded kernel modules.")
            return

    print(f"[*] Loaded modules: {len(modules)}")

    suspicious = [
        module for module in modules
        if any(term in module.lower() for term in SUSPICIOUS_NAMES)
    ]

    if suspicious:
        print("\n[!] Module names requiring investigation:")
        for module in suspicious:
            print(f"  {module}")
    else:
        print("[+] No known suspicious module names detected.")

    try:
        tainted = Path("/proc/sys/kernel/tainted").read_text().strip()
        print(f"\n[*] Kernel taint value: {tainted}")
        if tainted != "0":
            print("[!] A non-zero taint value requires review.")
    except OSError:
        pass

    show_all = input("\nShow all loaded modules? (y/N): ").strip().lower()
    if show_all == "y":
        for module in sorted(modules):
            print(f"  {module}")
