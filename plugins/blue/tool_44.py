import hashlib
import os
import time
from pathlib import Path

NAME = "Backup Verification Tool"
DESCRIPTION = "Verify backup integrity by comparing checksums."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("1. Generate checksums for a directory (create manifest)")
    print("2. Verify a directory against a manifest")
    choice = input("Select: ").strip()

    if choice == "1":
        create_manifest()
    elif choice == "2":
        verify_manifest()
    else:
        print("[!] Invalid choice.")


def sha256_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return "ERROR"


def create_manifest():
    directory = Path(input("Directory to hash: ").strip())
    if not directory.is_dir():
        print("[!] Not a valid directory.")
        return

    output = Path(input("Manifest output file (default backup_manifest.txt): ").strip()
                  or "backup_manifest.txt")

    print(f"[*] Hashing files in {directory}...")
    count = 0
    with open(output, "w", encoding="utf-8") as f:
        f.write(f"# Backup manifest created {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Source: {directory}\n\n")
        for item in sorted(directory.rglob("*")):
            if item.is_file():
                digest = sha256_file(item)
                rel = item.relative_to(directory)
                f.write(f"{digest}  {rel}\n")
                count += 1

    print(f"[+] Manifest written: {output} ({count} files)")


def verify_manifest():
    manifest = Path(input("Manifest file path: ").strip())
    if not manifest.is_file():
        print("[!] Manifest not found.")
        return

    directory = Path(input("Directory to verify against: ").strip())
    if not directory.is_dir():
        print("[!] Directory not found.")
        return

    lines = [
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

    ok = 0
    failures = 0

    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2:
            continue

        expected_hash, rel_path = parts
        full_path = directory / rel_path

        if not full_path.is_file():
            print(f"  [!] MISSING: {rel_path}")
            failures += 1
            continue

        actual = sha256_file(full_path)
        if actual != expected_hash:
            print(f"  [!] CHANGED: {rel_path}")
            failures += 1
        else:
            ok += 1

    print(f"\n[+] Verified: {ok} ok, {failures} failure(s)")
