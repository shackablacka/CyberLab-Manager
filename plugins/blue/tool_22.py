import gzip
import shutil
from pathlib import Path

NAME = "Log Archiver"
DESCRIPTION = "Compress old or large log files to save space."
ALLOWED_ROLES = ["admin", "instructor"]

LOG_DIR = Path("/var/log")
MIN_SIZE_MB = 5


def run(username, role):
    print("=== Log Archiver ===\n")
    candidates = []
    for f in LOG_DIR.glob("*"):
        if f.is_file() and not f.name.endswith(".gz") and not f.name.endswith(".xz"):
            size_mb = f.stat().st_size / 1024 / 1024
            if size_mb >= MIN_SIZE_MB:
                candidates.append((f, size_mb))

    if not candidates:
        print(f"[*] No logs >= {MIN_SIZE_MB} MB found in {LOG_DIR}")
        return

    print(f"{'#':<4}{'Size (MB)':<12}{'File'}")
    for i, (path, size) in enumerate(candidates, 1):
        print(f"{i:<4}{size:<12.1f}{path.name}")

    choice = input("\nSelect log to compress (0 = cancel): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(candidates)):
        return

    target, size = candidates[int(choice) - 1]
    confirm = input(f"gzip '{target.name}' ({size:.1f} MB)? (y/N): ").strip().lower()
    if confirm != "y":
        print("[!] Cancelled.")
        return

    print(f"[*] Compressing {target.name}...")
    with open(target, "rb") as f_in:
        with gzip.open(str(target) + ".gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out, 1024 * 1024)

    original = target.stat().st_size
    target.unlink()
    new_size = Path(str(target) + ".gz").stat().st_size
    saved = (original - new_size) / 1024 / 1024
    print(f"[+] Compressed {target.name} -> {target.name}.gz ({saved:.1f} MB saved)")
