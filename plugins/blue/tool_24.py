import json
import subprocess
from pathlib import Path

NAME = "USB Device Auditor"
DESCRIPTION = "List USB devices and flag newly connected hardware."
ALLOWED_ROLES = ["admin", "instructor", "student"]

BASELINE_DB = Path("database/usb_baseline.json")


def run(username, role):
    current = _usb_devices()
    if not current:
        print("[!] lsusb not available or no devices found.")
        return

    print(f"[*] {len(current)} USB device(s) present.\n")
    for dev in current:
        print(f"  {dev}")

    if BASELINE_DB.exists():
        baseline = set(json.loads(BASELINE_DB.read_text(encoding="utf-8")))
        now = set(current)
        new = now - baseline
        removed = baseline - now
        if new:
            print("\n[!] NEW USB devices detected:")
            for d in new:
                print(f"    [+] {d}")
        if removed:
            print("\n[-] USB devices removed:")
            for d in removed:
                print(f"    [-] {d}")
        if not new and not removed:
            print("\n[+] No USB changes since last snapshot.")
    else:
        print("\n[*] No baseline — this run creates it.")

    BASELINE_DB.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_DB.write_text(json.dumps(current, indent=2), encoding="utf-8")
    print(f"\n[+] Baseline saved: {BASELINE_DB}")


def _usb_devices():
    try:
        result = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=10)
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
