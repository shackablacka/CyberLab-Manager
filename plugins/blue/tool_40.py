import hashlib
import json
import subprocess
from pathlib import Path

NAME = "Security Baseline Comparator"
DESCRIPTION = "Snapshot key system state and compare future changes."
ALLOWED_ROLES = ["admin", "instructor"]

BASELINE = Path("database/security_baseline.json")
CONFIG_FILES = [
    Path("/etc/passwd"),
    Path("/etc/group"),
    Path("/etc/ssh/sshd_config"),
    Path("/etc/sudoers"),
    Path("/etc/hosts"),
]


def run(username, role):
    print("1. Create or replace baseline")
    print("2. Compare with existing baseline")
    choice = input("Select: ").strip()

    if choice == "1":
        state = collect_state()
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        print(f"[+] Baseline saved to {BASELINE}")
    elif choice == "2":
        if not BASELINE.exists():
            print("[!] No baseline exists. Create one first.")
            return
        compare_states(
            json.loads(BASELINE.read_text(encoding="utf-8")),
            collect_state(),
        )
    else:
        print("[!] Invalid choice.")


def sha256_file(path):
    if not path.is_file():
        return "MISSING"

    digest = hashlib.sha256()

    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
    except OSError:
        return "UNREADABLE"

    return digest.hexdigest()


def command_lines(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return result.stdout.splitlines()
        return [f"returncode={result.returncode}", *result.stderr.splitlines()]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [f"unavailable: {exc}"]


def collect_state():
    enabled_services = command_lines([
        "systemctl",
        "list-unit-files",
        "--state=enabled",
        "--type=service",
        "--no-legend",
        "--no-pager",
    ])

    return {
        "config_hashes": {
            str(path): sha256_file(path)
            for path in CONFIG_FILES
        },
        "routes": command_lines(["ip", "route"]),
        "listeners": command_lines(["ss", "-lntup"]),
        "enabled_services": enabled_services,
    }


def compare_states(old, new):
    changes = 0

    print("\n=== Configuration Changes ===")
    old_hashes = old.get("config_hashes", {})
    new_hashes = new.get("config_hashes", {})

    for path in sorted(set(old_hashes) | set(new_hashes)):
        if old_hashes.get(path) != new_hashes.get(path):
            print(f"  [!] Changed: {path}")
            changes += 1

    for label in ("routes", "listeners", "enabled_services"):
        old_values = set(old.get(label, []))
        new_values = set(new.get(label, []))

        for value in sorted(new_values - old_values)[:20]:
            print(f"  [+] {label}: {value}")
            changes += 1

        for value in sorted(old_values - new_values)[:20]:
            print(f"  [-] {label}: {value}")
            changes += 1

    if changes == 0:
        print("[+] No baseline changes detected.")
    else:
        print(f"\n[!] {changes} change(s) detected.")
