import os
import subprocess

NAME = "Privileged Process Auditor"
DESCRIPTION = "Review root processes and flag suspicious execution paths."
ALLOWED_ROLES = ["admin", "instructor"]

SUSPICIOUS_PATHS = ("/tmp/", "/var/tmp/", "/dev/shm/", "/run/user/")
SUSPICIOUS_NAMES = {"nc", "ncat", "netcat", "socat", "xmrig", "miner"}


def run(username, role):
    result = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,user=,uid=,comm=,args="],
        capture_output=True,
        text=True,
        timeout=10,
    )

    root_processes = []
    findings = []

    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 5)

        if len(parts) < 5:
            continue

        pid, ppid, user, uid, command = parts[:5]
        args = parts[5] if len(parts) == 6 else command

        if uid == "0":
            root_processes.append((pid, user, command, args))

            lower = f"{command} {args}".lower()

            if any(path in lower for path in SUSPICIOUS_PATHS):
                findings.append((pid, "temporary-directory execution", args))

            if any(name == command.lower() for name in SUSPICIOUS_NAMES):
                findings.append((pid, "suspicious process name", args))

            try:
                executable = os.readlink(f"/proc/{pid}/exe")
                if "(deleted)" in executable:
                    findings.append((pid, "deleted executable", executable))
            except OSError:
                pass

    print(f"[*] Root-owned processes: {len(root_processes)}")

    if findings:
        print("\n[!] Findings:")
        for pid, reason, detail in findings:
            print(f"  PID {pid:<8} {reason}: {detail[:160]}")
    else:
        print("[+] No obvious suspicious root-process indicators found.")

    show_root = input("\nShow root processes? (y/N): ").strip().lower()
    if show_root == "y":
        for pid, user, command, args in root_processes[:100]:
            print(f"  PID {pid:<8} {command:<24} {args[:120]}")
