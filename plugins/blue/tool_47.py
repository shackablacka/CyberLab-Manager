import shutil
import subprocess
from pathlib import Path

NAME = "Hardening Scorecard"
DESCRIPTION = "Quick security posture summary across key areas."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("=== System Hardening Scorecard ===\n")
    score = 0
    total = 0

    checks = [
        check_firewall,
        check_ssh,
        check_fail2ban,
        check_auto_updates,
        check_root_login,
        check_mac_framework,
        check_auditd,
        check_ntp,
    ]

    for check in checks:
        name, passed, detail = check()
        total += 1
        mark = "[+]" if passed else "[!]"
        if passed:
            score += 1
        print(f"  {mark} {name:<30} {detail}")

    percentage = (score / total * 100) if total else 0
    print(f"\n{'=' * 40}")
    print(f"  Score: {score}/{total} ({percentage:.0f}%)")

    if percentage >= 80:
        print("  Rating: GOOD")
    elif percentage >= 50:
        print("  Rating: NEEDS IMPROVEMENT")
    else:
        print("  Rating: POOR — review findings above")


def check_firewall():
    for tool in ("ufw", "iptables", "nft"):
        if shutil.which(tool):
            if tool == "ufw":
                r = subprocess.run(["ufw", "status"], capture_output=True,
                                   text=True, timeout=5)
                if "active" in r.stdout.lower():
                    return "Firewall", True, "ufw active"
                return "Firewall", False, "ufw installed but inactive"
            if tool == "iptables":
                r = subprocess.run(["iptables", "-L", "-n"],
                                   capture_output=True, text=True, timeout=5)
                rules = [l for l in r.stdout.splitlines()
                         if l and not l.startswith("Chain") and not l.startswith("target")]
                if rules:
                    return "Firewall", True, f"iptables ({len(rules)} rules)"
                return "Firewall", False, "iptables: no rules"
    return "Firewall", False, "no firewall tool found"


def check_ssh():
    config = Path("/etc/ssh/sshd_config")
    if not config.exists():
        return "SSH Hardening", True, "sshd not installed"
    content = config.read_text(errors="ignore").lower()
    root_ok = "permitrootlogin no" in content or "permitrootlogin prohibit-password" in content
    return "SSH Hardening", root_ok, "root login restricted" if root_ok else "root login may be allowed"


def check_fail2ban():
    if not shutil.which("fail2ban-client"):
        return "Fail2Ban", False, "not installed"
    r = subprocess.run(["systemctl", "is-active", "fail2ban"],
                       capture_output=True, text=True, timeout=5)
    active = r.stdout.strip() == "active"
    return "Fail2Ban", active, "active" if active else "inactive"


def check_auto_updates():
    if shutil.which("unattended-upgrade"):
        return "Auto Updates", True, "unattended-upgrades present"
    return "Auto Updates", False, "unattended-upgrades not installed"


def check_root_login():
    try:
        shadow = Path("/etc/shadow").read_text(errors="ignore")
        for line in shadow.splitlines():
            if line.startswith("root:"):
                h = line.split(":")[1]
                if h in ("*", "!", "!!", ""):
                    return "Root Password", True, "root account locked"
                return "Root Password", False, "root has a password set"
    except PermissionError:
        pass
    return "Root Password", False, "could not read /etc/shadow"


def check_mac_framework():
    if Path("/sys/module/apparmor").exists():
        return "MAC Framework", True, "AppArmor loaded"
    if shutil.which("getenforce"):
        r = subprocess.run(["getenforce"], capture_output=True, text=True, timeout=5)
        if "enforcing" in r.stdout.lower():
            return "MAC Framework", True, "SELinux enforcing"
        return "MAC Framework", False, f"SELinux {r.stdout.strip()}"
    return "MAC Framework", False, "none detected"


def check_auditd():
    if not shutil.which("auditctl"):
        return "Audit Framework", False, "auditd not installed"
    r = subprocess.run(["systemctl", "is-active", "auditd"],
                       capture_output=True, text=True, timeout=5)
    active = r.stdout.strip() == "active"
    return "Audit Framework", active, "active" if active else "inactive"


def check_ntp():
    r = subprocess.run(["timedatectl", "show", "-p", "NTPSynchronized"],
                       capture_output=True, text=True, timeout=5)
    synced = "yes" in r.stdout.lower()
    return "NTP Sync", synced, "synchronized" if synced else "NOT synchronized"
