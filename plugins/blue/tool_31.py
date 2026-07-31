import os
import shutil
import subprocess
from pathlib import Path

NAME = "Systemd Service Hardening Auditor"
DESCRIPTION = "Review enabled services for risky paths and permissions."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    if not shutil.which("systemctl"):
        print("[!] systemctl is unavailable.")
        return

    result = subprocess.run(
        [
            "systemctl", "list-unit-files",
            "--state=enabled",
            "--type=service",
            "--no-legend",
            "--no-pager",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )

    if result.returncode != 0:
        print("[!] Could not list enabled services.")
        return

    units = [
        line.split()[0]
        for line in result.stdout.splitlines()
        if line.split() and line.split()[0].endswith(".service")
    ]

    print(f"[*] Reviewing {len(units)} enabled service(s)...")
    findings = []

    for unit in units:
        show = subprocess.run(
            [
                "systemctl",
                "show",
                unit,
                "-p", "User",
                "-p", "ExecStart",
                "-p", "FragmentPath",
                "--no-pager",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        properties = {}
        for line in show.stdout.splitlines():
            key, separator, value = line.partition("=")
            if separator:
                properties[key] = value

        exec_start = properties.get("ExecStart", "")
        fragment = properties.get("FragmentPath", "")
        combined = f"{exec_start} {fragment}".lower()

        risky_path = any(
            path in combined
            for path in ("/tmp/", "/var/tmp/", "/dev/shm/", "/run/user/")
        )

        writable_unit = False
        if fragment and Path(fragment).is_file():
            mode = os.stat(fragment).st_mode
            writable_unit = bool(mode & 0o022)

        if risky_path or writable_unit:
            reasons = []
            if risky_path:
                reasons.append("temporary-path execution")
            if writable_unit:
                reasons.append("unit file is group/world writable")

            findings.append((unit, ", ".join(reasons)))

    if not findings:
        print("[+] No obvious service hardening findings detected.")
        return

    print("\n[!] Services requiring review:")
    for unit, reason in findings:
        print(f"  {unit:<40} {reason}")
