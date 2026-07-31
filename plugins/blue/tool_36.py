import shutil
import subprocess
from pathlib import Path

NAME = "Sudoers Configuration Auditor"
DESCRIPTION = "Review sudoers entries for overly broad privileges."
ALLOWED_ROLES = ["admin", "instructor"]

SUDOERS = Path("/etc/sudoers")
SUDOERS_DIR = Path("/etc/sudoers.d")


def run(username, role):
    files = []

    if SUDOERS.is_file():
        files.append(SUDOERS)

    if SUDOERS_DIR.is_dir():
        files.extend(
            path for path in sorted(SUDOERS_DIR.iterdir())
            if path.is_file()
        )

    if not files:
        print("[!] No sudoers files found.")
        return

    if shutil.which("visudo"):
        check = subprocess.run(
            ["visudo", "-c"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = check.stdout or check.stderr
        print("=== visudo syntax check ===")
        print(output or "(no output)")

    findings = []

    for path in files:
        try:
            lines = path.read_text(errors="ignore").splitlines()
        except PermissionError:
            print(f"[!] Cannot read {path}.")
            continue

        for line in lines:
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            upper = stripped.upper()

            if "NOPASSWD:" in upper:
                findings.append((path, "NOPASSWD privilege", stripped))

            if "!AUTHENTICATE" in upper:
                findings.append((path, "authentication disabled", stripped))

            if "SETENV:" in upper:
                findings.append((path, "SETENV enabled", stripped))

            if "ALL=(ALL" in upper:
                findings.append((path, "broad ALL command scope", stripped))

    print("\n=== Review Findings ===")

    if not findings:
        print("[+] No obvious high-risk sudoers patterns found.")
        return

    for path, reason, line in findings:
        print(f"  [!] {path}: {reason}")
        print(f"      {line[:180]}")
