import json
import shutil
import subprocess
import time
from pathlib import Path

NAME = "Evidence Collector"
DESCRIPTION = "Snapshot volatile system state for forensic preservation."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/blue/reports")


def run(username, role):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = REPORT_DIR / f"evidence_{timestamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Collecting volatile evidence to {out_dir}...\n")

    commands = {
        "date": ["date", "-u"],
        "uptime": ["uptime"],
        "uname": ["uname", "-a"],
        "who": ["who"],
        "last_logins": ["last", "-a", "-n", "30"],
        "ps_full": ["ps", "auxf"],
        "network_connections": ["ss", "-tunap"],
        "listening_ports": ["ss", "-lntup"],
        "routing_table": ["ip", "route"],
        "arp_table": ["ip", "neigh"],
        "interfaces": ["ip", "-o", "addr"],
        "dns_config": ["cat", "/etc/resolv.conf"],
        "loaded_modules": ["lsmod"],
        "mounts": ["mount"],
        "disk_usage": ["df", "-h"],
        "env_variables": ["env"],
    }

    summary = {"timestamp": timestamp, "files": []}

    for name, cmd in commands.items():
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15
            )
            content = result.stdout or result.stderr or "(no output)"
        except (OSError, subprocess.TimeoutExpired) as e:
            content = f"Error: {e}"

        file_path = out_dir / f"{name}.txt"
        file_path.write_text(content, encoding="utf-8")
        summary["files"].append(name)
        print(f"  [+] {name}")

    # Copy key config files
    config_files = ["/etc/passwd", "/etc/group", "/etc/hosts",
                    "/etc/ssh/sshd_config", "/etc/sudoers"]
    config_dir = out_dir / "configs"
    config_dir.mkdir(exist_ok=True)

    for src in config_files:
        src_path = Path(src)
        if src_path.is_file():
            try:
                shutil.copy2(src_path, config_dir / src_path.name)
                print(f"  [+] config: {src}")
            except PermissionError:
                print(f"  [-] config: {src} (permission denied)")

    # Auth log snippet
    for log_path in [Path("/var/log/auth.log"), Path("/var/log/secure")]:
        if log_path.exists():
            try:
                lines = log_path.read_text(errors="ignore").splitlines()
                tail = "\n".join(lines[-200:])
                (out_dir / "auth_log_tail.txt").write_text(tail, encoding="utf-8")
                print(f"  [+] auth log tail ({len(lines[-200:])} lines)")
            except PermissionError:
                print(f"  [-] {log_path} (permission denied)")
            break

    manifest = out_dir / "manifest.json"
    manifest.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\n[+] Evidence collection complete: {out_dir}")
    print(f"[*] {len(summary['files'])} artifacts collected.")
    print(f"[*] Preserve this directory for incident documentation.")
