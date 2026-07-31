import stat
from pathlib import Path

NAME = "Weak File Permissions Finder"
DESCRIPTION = "Check sensitive files for overly permissive permissions."
ALLOWED_ROLES = ["admin", "instructor"]

CHECKS = [
    Path("/etc/shadow"),
    Path("/etc/passwd"),
    Path("/etc/ssh/sshd_config"),
    Path("/etc/sudoers"),
    Path("/etc/gshadow"),
]

HOME_DIRS = [Path("/home")]


def run(username, role):
    print("=== Weak File Permissions ===\n")
    issues = 0

    for path in CHECKS:
        if not path.exists():
            continue
        mode = stat.S_IMODE(path.stat().st_mode)
        perms = oct(mode)[-3:]
        if mode & 0o004 or mode & 0o002:
            print(f"  [!] {path} is world-readable/writable ({perms})")
            issues += 1
        else:
            print(f"  [+] {path} permissions ok ({perms})")

    # SSH private keys in home dirs
    for home in HOME_DIRS:
        if not home.is_dir():
            continue
        for key in home.rglob("*.pem"):
            mode = stat.S_IMODE(key.stat().st_mode)
            if mode & 0o044:
                print(f"  [!] Private key world-readable: {key} "
                      f"(perm {oct(mode)[-3:]})")
                issues += 1
        ssh_dir = home / ".ssh"
        if ssh_dir.is_dir():
            for key in ssh_dir.glob("id_*"):
                if key.name.endswith(".pub"):
                    continue
                mode = stat.S_IMODE(key.stat().st_mode)
                if mode & 0o044:
                    print(f"  [!] SSH key world-readable: {key}")
                    issues += 1

    if issues == 0:
        print("  [+] No weak permissions found.")
    else:
        print(f"\n[!] {issues} issue(s) found. Fix with chmod.")
