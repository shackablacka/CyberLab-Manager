import subprocess
import time

NAME = "Process Watcher"
DESCRIPTION = "Watch for new processes over a short interval."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    raw = input("Watch duration in seconds (default 30): ").strip()
    duration = int(raw) if raw.isdigit() else 30

    initial = _get_processes()
    print(f"[*] Baseline: {len(initial)} processes running.")
    print(f"[*] Watching for new processes for {duration}s (Ctrl+C to stop)...\n")

    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("[!] Watch interrupted.")

    current = _get_processes()
    new_pids = set(current) - set(initial)
    gone_pids = set(initial) - set(current)

    print(f"\n[+] Processes started during window: {len(new_pids)}")
    for pid in sorted(new_pids):
        name, user = current[pid]
        print(f"    [+] PID {pid:<6} {name:<25} user={user}")

    print(f"[-] Processes ended during window: {len(gone_pids)}")
    for pid in sorted(gone_pids)[:15]:
        name, user = initial[pid]
        print(f"    [-] PID {pid:<6} {name:<25} user={user}")

    if not new_pids:
        print("    (none)")


def _get_processes():
    result = subprocess.run(["ps", "-eo", "pid=,user=,comm="],
                            capture_output=True, text=True, timeout=10)
    procs = {}
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) == 3:
            pid, user, comm = parts
            procs[pid] = (comm, user)
    return procs
