import hashlib
import json
from pathlib import Path

NAME = "File Integrity Monitor"
DESCRIPTION = "Baseline a directory's hashes, then detect changes."
ALLOWED_ROLES = ["admin", "instructor", "student"]

BASELINE_DB = Path("database/fim_baseline.json")


def run(username, role):
    print("1. Create baseline")
    print("2. Check integrity")
    choice = input("Select: ").strip()

    target = Path(input("Directory (default core/): ").strip() or "core")
    if not target.is_dir():
        print("[!] Directory not found.")
        return

    if choice == "1":
        create_baseline(target)
    elif choice == "2":
        check_integrity(target)
    else:
        print("[!] Invalid choice.")


def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return ""


def snapshot(directory):
    hashes = {}
    for item in directory.rglob("*"):
        if item.is_file():
            digest = hash_file(item)
            if digest:
                hashes[str(item)] = digest
    return hashes


def create_baseline(directory):
    print(f"[*] Hashing {directory} ...")
    hashes = snapshot(directory)
    BASELINE_DB.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_DB.write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    print(f"[+] Baseline saved: {BASELINE_DB} ({len(hashes)} files)")


def check_integrity(directory):
    if not BASELINE_DB.exists():
        print("[!] No baseline found — create one first.")
        return

    baseline = json.loads(BASELINE_DB.read_text(encoding="utf-8"))
    current = snapshot(directory)

    modified = [f for f in baseline if f in current and baseline[f] != current[f]]
    added = [f for f in current if f not in baseline]
    deleted = [f for f in baseline if f not in current]

    for f in modified:
        print(f"  [!] MODIFIED: {f}")
    for f in added:
        print(f"  [+] NEW:      {f}")
    for f in deleted:
        print(f"  [-] DELETED:  {f}")

    if not (modified or added or deleted):
        print("[+] Integrity verified — no changes detected.")
    else:
        print(f"\n[!] {len(modified)} modified, {len(added)} new, "
              f"{len(deleted)} deleted.")
