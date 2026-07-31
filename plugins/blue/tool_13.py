from pathlib import Path

NAME = "SSH Hardening Auditor"
DESCRIPTION = "Audit sshd_config for insecure settings."
ALLOWED_ROLES = ["admin", "instructor"]

CONFIG_PATHS = [Path("/etc/ssh/sshd_config"),
                Path("/etc/ssh/sshd_config.d/")]

CHECKS = {
    "PermitRootLogin": (["no", "prohibit-password"], "Disable root login"),
    "PasswordAuthentication": (["no"], "Use keys instead of passwords"),
    "X11Forwarding": (["no"], "Disable X11 forwarding"),
    "UsePAM": (["yes"], "Keep PAM enabled"),
    "Protocol": (["2"], "Only SSH2"),
    "MaxAuthTries": (["3", "4"], "Limit auth retries"),
    "PubkeyAuthentication": (["yes"], "Enable public key auth"),
}


def run(username, role):
    target = None
    for p in CONFIG_PATHS:
        if p.is_file():
            target = p
            break
    if not target:
        print("[!] sshd_config not found.")
        return

    try:
        lines = target.read_text(errors="ignore").splitlines()
    except PermissionError:
        print("[!] Permission denied — run as root.")
        return

    # Include drop-in configs
    drop_dir = Path("/etc/ssh/sshd_config.d/")
    if drop_dir.is_dir():
        for f in sorted(drop_dir.glob("*.conf")):
            try:
                lines += f.read_text(errors="ignore").splitlines()
            except PermissionError:
                continue

    print(f"=== SSH Hardening Audit ({target}) ===\n")
    found = {key: None for key in CHECKS}
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and " " in line:
            key, _, value = line.partition(" ")
            key = key.strip()
            value = value.strip()
            if key in found:
                found[key] = value

    issues = 0
    for key, (good_values, hint) in CHECKS.items():
        value = found[key]
        if value is None:
            print(f"  [-] {key:<28} NOT SET — {hint}")
            issues += 1
        elif value in good_values:
            print(f"  [+] {key:<28} {value} (good)")
        else:
            print(f"  [!] {key:<28} {value} — {hint}")
            issues += 1

    # Check for Match blocks or other overrides (simplistic)
    print("\n--- Additional Checks ---")
    for line in lines:
        if line.lower().startswith("include "):
            print(f"  [i] Include directive: {line}")

    if issues == 0:
        print("\n[+] No obvious issues found.")
    else:
        print(f"\n[!] {issues} issue(s) found — review hardening guidelines.")
