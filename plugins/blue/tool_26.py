import subprocess

NAME = "Boot Services Auditor"
DESCRIPTION = "List enabled systemd services and flag non-standard ones."
ALLOWED_ROLES = ["admin", "instructor"]

KNOWN_BASIC = {
    "accounts-daemon.service", "acpid.service", "apparmor.service", "avahi-daemon.service",
    "bluetooth.service", "cron.service", "cups.service", "dbus.service", "fail2ban.service",
    "NetworkManager.service", "rsyslog.service", "ssh.service", "systemd-journald.service",
    "systemd-logind.service", "systemd-networkd.service", "systemd-timesyncd.service",
    "udisks2.service", "unattended-upgrades.service", "user@1000.service", "whoopsie.service",
}


def run(username, role):
    result = subprocess.run(["systemctl", "list-unit-files", "--state=enabled",
                             "--type=service", "--no-legend", "--no-pager"],
                            capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        print("[!] systemctl failed (are you on a systemd distro?).")
        return

    services = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if parts:
            services.append(parts[0])

    print(f"[+] {len(services)} enabled services.\n")

    unknown = []
    for name in sorted(services):
        if name in KNOWN_BASIC:
            print(f"  [i] {name}")
        else:
            print(f"  [?] {name}")
            unknown.append(name)

    if unknown:
        print(f"\n[!] {len(unknown)} not in known-basic list. Investigate:")
        for name in unknown:
            print(f"    {name}")
    else:
        print("\n[+] All services are commonly expected.")
