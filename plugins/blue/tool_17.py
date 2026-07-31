from pathlib import Path

NAME = "Log Rotation Auditor"
DESCRIPTION = "Check logrotate config for log sizes and missing options."
ALLOWED_ROLES = ["admin", "instructor"]

LOG_DIRS = [Path("/var/log")]
CONFIGS = [Path("/etc/logrotate.conf"), Path("/etc/logrotate.d")]


def run(username, role):
    # Find big logs
    print("=== Largest Log Files ===")
    log_files = []
    for d in LOG_DIRS:
        if d.is_dir():
            for f in d.rglob("*"):
                if f.is_file() and f.stat().st_size > 10 * 1024 * 1024:
                    log_files.append((f, f.stat().st_size))
    log_files.sort(key=lambda x: -x[1])
    for f, size in log_files[:5]:
        print(f"  {size/1024/1024:7.1f} MB  {f}")

    # Check logrotate configs
    print("\n=== Logrotate Config Checks ===")
    missing = 0
    for c in CONFIGS:
        files = []
        if c.is_file():
            files = [c]
        elif c.is_dir():
            files = list(c.glob("*"))
        for cf in files:
            content = cf.read_text(errors="ignore")
            lines = content.splitlines()
            for line in lines:
                if "daily" in line.lower() and "size" not in line.lower():
                    pass  # daily can be okay
                # Check for missing compress
                if "compress" not in content.lower():
                    print(f"  [!] {cf}: missing 'compress' option")
                    missing += 1
                    break

    if missing == 0:
        print("  [+] Good: compression configured in all active configs.")
    print("\n[*] Review /etc/logrotate.conf for global settings.")
