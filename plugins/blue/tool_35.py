import time
from pathlib import Path

NAME = "File Change Watcher"
DESCRIPTION = "Monitor a directory for created, modified, or deleted files."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def snapshot(directory):
    state = {}

    for item in directory.rglob("*"):
        if item.is_symlink() or not item.is_file():
            continue

        try:
            info = item.stat()
            state[str(item)] = (info.st_size, info.st_mtime_ns)
        except OSError:
            continue

    return state


def run(username, role):
    raw_path = input("Directory to watch (default core/): ").strip()
    directory = Path(raw_path or "core")

    if not directory.is_dir():
        print("[!] Directory does not exist.")
        return

    raw_duration = input("Duration in seconds (default 20): ").strip()
    duration = int(raw_duration) if raw_duration.isdigit() else 20

    before = snapshot(directory)
    print(f"[*] Watching {directory} for {duration} seconds...")

    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("\n[!] Watch interrupted.")

    after = snapshot(directory)

    before_files = set(before)
    after_files = set(after)

    created = sorted(after_files - before_files)
    deleted = sorted(before_files - after_files)
    modified = sorted(
        path for path in before_files & after_files
        if before[path] != after[path]
    )

    print("\n=== File Changes ===")

    for path in created:
        print(f"  [+] CREATED:  {path}")

    for path in modified:
        print(f"  [!] MODIFIED: {path}")

    for path in deleted:
        print(f"  [-] DELETED:  {path}")

    if not any((created, modified, deleted)):
        print("  [+] No changes detected.")
    else:
        print(
            f"\n[!] Summary: {len(created)} created, "
            f"{len(modified)} modified, {len(deleted)} deleted."
        )
