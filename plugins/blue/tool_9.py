import json
import subprocess
from pathlib import Path

NAME = "Connection Diff Monitor"
DESCRIPTION = "Snapshot active connections, diff against previous state."
ALLOWED_ROLES = ["admin", "instructor", "student"]

SNAPSHOT_DB = Path("database/conn_snapshot.json")


def run(username, role):
    current = _get_connections()
    print(f"[*] {len(current)} active TCP/UDP connection(s) right now.")

    if SNAPSHOT_DB.exists():
        previous = set(json.loads(SNAPSHOT_DB.read_text(encoding="utf-8")))
        now = set(current)
        new = sorted(now - previous)
        closed = sorted(previous - now)

        print("\n--- Changes since last snapshot ---")
        for c in new:
            print(f"  [+] NEW:    {c}")
        for c in closed:
            print(f"  [-] CLOSED: {c}")
        if not new and not closed:
            print("  [+] No changes detected.")
    else:
        print("\n[*] No previous snapshot — this run creates the baseline.")
        for c in current[:15]:
            print(f"  {c}")
        if len(current) > 15:
            print(f"  ... and {len(current) - 15} more.")

    SNAPSHOT_DB.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DB.write_text(json.dumps(current, indent=2), encoding="utf-8")
    print(f"\n[+] Snapshot saved: {SNAPSHOT_DB}")


def _get_connections():
    for cmd, args in (("ss", ["-tunp"]), ("netstat", ["-tunp"])):
        try:
            result = subprocess.run([cmd] + args, capture_output=True,
                                    text=True, timeout=10)
            if result.returncode == 0:
                return [l.strip() for l in result.stdout.splitlines()[2:]
                        if l.strip()]
        except FileNotFoundError:
            continue
    return []
