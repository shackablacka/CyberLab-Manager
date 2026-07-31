import subprocess
from pathlib import Path
from core.tool_runner import is_installed

NAME = "Suricata Rule Check"
DESCRIPTION = "Check Suricata rule file and count rules."
ALLOWED_ROLES = ["admin", "instructor"]

RULE_DIRS = [Path("/var/lib/suricata/rules"),
             Path("/etc/suricata/rules"),
             Path("/usr/share/suricata/rules")]


def run(username, role):
    if not is_installed("suricata"):
        print("[!] suricata not installed.")
        return

    # Find rule files
    rules = []
    for d in RULE_DIRS:
        if d.is_dir():
            for f in d.glob("*.rules"):
                rules.append(f)

    if not rules:
        print("[!] No rule files found in standard locations.")
        return

    print(f"[+] Found {len(rules)} rule file(s).\n")
    for f in rules:
        try:
            count = sum(1 for line in f.read_text(errors="ignore").splitlines()
                        if line.strip() and not line.startswith("#"))
            print(f"  {f:<60} {count:>6} rules")
        except PermissionError:
            print(f"  {f:<60} (unreadable)")

    # Check version
    result = subprocess.run(["suricata", "--build-info"],
                            capture_output=True, text=True, timeout=5)
    for line in (result.stdout or "").splitlines():
        if "Version" in line or "version" in line:
            print(f"\n  Suricata: {line.strip()}")

    print("\n[*] Update rules with: suricata-update   (if installed)")
