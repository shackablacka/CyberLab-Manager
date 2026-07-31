"""Admin-only lab tool installation and status checks."""

import shutil
import subprocess

RED_TOOLS = {
    "nmap": "nmap",
    "masscan": "masscan",
    "nikto": "nikto",
    "dirb": "dirb",
    "gobuster": "gobuster",
    "feroxbuster": "feroxbuster",
    "wfuzz": "wfuzz",
    "hydra": "hydra",
    "medusa": "medusa",
    "ncrack": "ncrack",
    "john": "john",
    "hashcat": "hashcat",
    "sqlmap": "sqlmap",
    "metasploit-framework": "metasploit-framework",
    "msfconsole": "metasploit-framework",
    "beef-xss": "beef-xss",
    "responder": "responder",
    "impacket-secretsdump": "impacket-scripts",
    "crackmapexec": "crackmapexec",
    "enum4linux": "enum4linux-ng",
    "smbclient": "smbclient",
    "rpcclient": "smbclient",
    "nbtscan": "nbtscan",
    "onesixtyone": "onesixtyone",
    "snmpwalk": "snmp",
    "dnsenum": "dnsenum",
    "fierce": "fierce",
    "amass": "amass",
    "subfinder": "subfinder",
    "wpscan": "wpscan",
    "joomscan": "joomscan",
    "droopescan": "droopescan",
    "whatweb": "whatweb",
    "wapiti": "wapiti",
    "skipfish": "skipfish",
    "arachni": "arachni",
    "burpsuite": "burpsuite",
    "zaproxy": "zaproxy",
    "aircrack-ng": "aircrack-ng",
    "kismet": "kismet",
    "wifite": "wifite",
    "ettercap": "ettercap-graphical",
    "bettercap": "bettercap",
    "yara": "yara",
    "binwalk": "binwalk",
    "foremost": "foremost",
    "steghide": "steghide",
    "exiftool": "libimage-exiftool-perl",
    "pdfid": "pdfid",
    "pdf-parser": "pdf-parser",
    "setoolkit": "set",
}

BLUE_TOOLS = {
    "snort": "snort",
    "suricata": "suricata",
    "zeek": "zeek",
    "fail2ban-client": "fail2ban",
    "rkhunter": "rkhunter",
    "chkrootkit": "chkrootkit",
    "lynis": "lynis",
    "clamscan": "clamav",
    "aide": "aide",
    "auditctl": "auditd",
    "ausearch": "auditd",
    "aureport": "auditd",
    "psad": "psad",
    "tripwire": "tripwire",
    "samhain": "samhain",
    "ossec": "ossec-hids",
    "logwatch": "logwatch",
    "swatch": "swatch",
    "argus": "argus",
    "tcpdump": "tcpdump",
    "wireshark": "wireshark",
    "tshark": "tshark",
    "ngrep": "ngrep",
    "netstat": "net-tools",
    "ss": "iproute2",
    "lsof": "lsof",
    "htop": "htop",
    "iotop": "iotop",
    "glances": "glances",
    "nethogs": "nethogs",
    "iftop": "iftop",
    "iptraf-ng": "iptraf-ng",
    "vnstat": "vnstat",
    "logrotate": "logrotate",
    "rsyslogd": "rsyslog",
    "syslog-ng": "syslog-ng",
    "journalctl": "systemd",
    "firewalld": "firewalld",
    "ufw": "ufw",
    "iptables": "iptables",
    "nft": "nftables",
    "tcp_wrappers": "tcpd",
    "portsentry": "portsentry",
    "tripwire-check": "tripwire",
    "debsums": "debsums",
    "needrestart": "needrestart",
    "unattended-upgrade": "unattended-upgrades",
    "apticron": "apticron",
    "chkconfig": "sysv-rc-conf",
    "sensors": "lm-sensors",
    "smartctl": "smartmontools",
    "hdparm": "hdparm",
}

ALL_TOOLS = {**RED_TOOLS, **BLUE_TOOLS}


def run(username: str, role: str) -> None:
    if role != "admin":
        print("[!] Admin privileges required.")
        return

    while True:
        print("\n=== Lab Setup & Maintenance ===")
        print("1. Install Red Team tools")
        print("2. Install Blue Team tools")
        print("3. Install all tools")
        print("4. Check tool status")
        print("0. Back")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            return
        if choice == "1":
            install_group("Red Team", RED_TOOLS)
        elif choice == "2":
            install_group("Blue Team", BLUE_TOOLS)
        elif choice == "3":
            install_group("All", ALL_TOOLS)
        elif choice == "4":
            check_status(ALL_TOOLS)
        else:
            print("[!] Invalid option.")


def install_group(label: str, tools: dict[str, str]) -> None:
    print(f"\n=== {label} Tool Installation ===")

    if shutil.which("apt-get") is None:
        print("[!] apt-get is unavailable on this OS.")
        return

    confirm = input(
        f"Install up to {len(tools)} {label} packages? (y/N): "
    ).strip().lower()

    if confirm != "y":
        print("[!] Installation cancelled.")
        return

    print("[*] Updating package index...")
    result = subprocess.run(["sudo", "apt-get", "update"], check=False)

    if result.returncode != 0:
        print("[!] apt-get update failed.")
        return

    failures = []

    for binary, package in tools.items():
        if shutil.which(binary):
            print(f"[+] {binary:<25} already installed")
            continue

        print(f"[*] Installing {package}...")
        result = subprocess.run(
            ["sudo", "apt-get", "install", "-y", package],
            check=False,
        )

        if result.returncode == 0:
            print(f"[+] {package:<25} installed")
        else:
            print(f"[!] Failed to install {package}")
            failures.append(package)

    if failures:
        print("\n[!] Failed packages:")
        for pkg in failures:
            print(f"    - {pkg}")
    else:
        print("\n[+] Installation process complete.")


def check_status(tools: dict[str, str]) -> None:
    print("\n=== Tool Status ===")
    print(f"{'Binary':<28}{'Status':<12}{'apt package'}")
    print("-" * 60)

    for binary, package in tools.items():
        if shutil.which(binary):
            print(f"{binary:<28}{'installed':<12}{package}")
        else:
            print(f"{binary:<28}{'missing':<12}{package}")
