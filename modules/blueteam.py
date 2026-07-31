"""Blue Team module - 50 defensive security tools."""

import logging
from pathlib import Path
from modules.tool_runner import execute_tool, sanitize, get_user_id, \
    check_tool, run_command, save_scan, save_event

log = logging.getLogger("cyberlab.blueteam")


def _journalctl_handler(username, tool_def, team):
    print("\n1. Recent errors  2. Auth logs  3. Kernel  4. Custom unit")
    c = input("Select: ").strip()
    flags = {
        "1": ["-p", "err", "-n", "100", "--no-pager"],
        "2": ["-u", "ssh", "-n", "100", "--no-pager"],
        "3": ["-k", "-n", "100", "--no-pager"],
    }.get(c, ["-n", "100", "--no-pager"])
    if c == "4":
        unit = sanitize(input("Unit name: ").strip())
        if unit:
            flags = ["-u", unit, "-n", "100", "--no-pager"]
    cmd = ["journalctl"] + flags
    uid = get_user_id(username)
    out, rc = run_command(cmd, 30)
    save_scan(uid, "journalctl", "local", " ".join(flags), out, "completed", team)
    print(out[:3000])


def _logwatch_handler(username, tool_def, team):
    cmd = ["logwatch", "--detail", "high", "--range", "today"]
    uid = get_user_id(username)
    out, rc = run_command(cmd, 120)
    save_scan(uid, "logwatch", "local", "--detail high", out, "completed", team)
    print(out[:3000])


def _chkrootkit_handler(username, tool_def, team):
    cmd = ["chkrootkit", "-q"]
    uid = get_user_id(username)
    print("[*] Running chkrootkit (this takes a minute)...")
    out, rc = run_command(cmd, 300)
    save_scan(uid, "chkrootkit", "local", "-q", out, "completed", team)
    save_event("rootkit_scan", "high" if "INFECTED" in out else "info",
               "local", "chkrootkit scan completed", out[:5000])
    print(out[:3000])


def _rkhunter_handler(username, tool_def, team):
    cmd = ["rkhunter", "--check", "--skip-keypress", "--report-warnings-only"]
    uid = get_user_id(username)
    print("[*] Running rkhunter (this takes a minute)...")
    out, rc = run_command(cmd, 300)
    save_scan(uid, "rkhunter", "local", "--check", out, "completed", team)
    save_event("rootkit_scan", "high" if "Warning" in out else "info",
               "local", "rkhunter scan completed", out[:5000])
    print(out[:3000])


def _lynis_handler(username, tool_def, team):
    cmd = ["lynis", "audit", "system", "--quick"]
    uid = get_user_id(username)
    print("[*] Running Lynis audit (this takes a few minutes)...")
    out, rc = run_command(cmd, 600)
    save_scan(uid, "lynis", "local", "audit system", out, "completed", team)
    save_event("security_audit", "info", "local", "Lynis system audit", out[:5000])
    print(out[:3000])


def _clamscan_handler(username, tool_def, team):
    target = sanitize(input("Path to scan [/home]: ").strip()) or "/home"
    cmd = ["clamscan", "-r", "--infected", target]
    uid = get_user_id(username)
    print(f"[*] Scanning {target}...")
    out, rc = run_command(cmd, 900)
    save_scan(uid, "clamscan", target, "-r --infected", out, "completed", team)
    sev = "high" if "Infected files:" in out and "Infected files: 0" not in out else "info"
    save_event("malware_scan", sev, target, "ClamAV scan completed", out[:5000])
    print(out[:3000])


def _yara_handler(username, tool_def, team):
    rules = sanitize(input("YARA rules file: ").strip())
    target = sanitize(input("Path to scan: ").strip())
    if not rules or not target:
        print("[!] Both rules and target required.")
        return
    cmd = ["yara", "-r", rules, target]
    uid = get_user_id(username)
    out, rc = run_command(cmd, 300)
    save_scan(uid, "yara", target, rules, out, "completed", team)
    print(out[:3000])


def _iptables_handler(username, tool_def, team):
    print("\n1. List rules  2. List with counters  3. NAT rules  4. Flush all (DANGEROUS)")
    c = input("Select: ").strip()
    cmds = {
        "1": ["iptables", "-L", "-n", "-v"],
        "2": ["iptables", "-L", "-n", "-v", "-x"],
        "3": ["iptables", "-t", "nat", "-L", "-n", "-v"],
        "4": ["iptables", "-F"],
    }
    if c not in cmds:
        return
    if c == "4":
        confirm = input("This will remove ALL firewall rules. Type 'yes': ").strip()
        if confirm != "yes":
            return
    cmd = cmds[c]
    uid = get_user_id(username)
    out, rc = run_command(cmd, 30)
    save_scan(uid, "iptables", "local", " ".join(cmd[1:]), out, "completed", team)
    save_event("firewall_audit", "info", "local", f"iptables {' '.join(cmd[1:])}", out[:5000])
    print(out[:3000])


def _aide_handler(username, tool_def, team):
    print("\n1. Initialize database  2. Check integrity")
    c = input("Select: ").strip()
    if c == "1":
        cmd = ["aide", "--init"]
    elif c == "2":
        cmd = ["aide", "--check"]
    else:
        return
    uid = get_user_id(username)
    print("[*] Running AIDE (this takes a while)...")
    out, rc = run_command(cmd, 600)
    save_scan(uid, "aide", "local", c, out, "completed", team)
    save_event("integrity_check", "high" if "differences" in out.lower() else "info",
               "local", "AIDE integrity check", out[:5000])
    print(out[:3000])


def _dd_handler(username, tool_def, team):
    src = sanitize(input("Source device (e.g. /dev/sda1): ").strip())
    dst = sanitize(input("Output file (e.g. /tmp/disk.img): ").strip())
    if not src or not dst:
        return
    bs = sanitize(input("Block size [4M]: ").strip()) or "4M"
    cmd = ["dd", f"if={src}", f"of={dst}", f"bs={bs}", "status=progress"]
    uid = get_user_id(username)
    print(f"[*] Imaging {src} to {dst}...")
    out, rc = run_command(cmd, 3600)
    save_scan(uid, "dd", src, f"of={dst}", out, "completed", team)
    print(out[:2000])


BLUE_TOOLS = {
    "Network Monitoring": {
        "tcpdump":    {"binary": "tcpdump",     "desc": "Packet capture",        "flags": ["-i", "eth0", "-c", "100", "-nn"], "target": False, "timeout": 120},
        "tshark":     {"binary": "tshark",      "desc": "Wireshark CLI",         "flags": ["-i", "eth0", "-c", "50"], "target": False, "timeout": 120},
        "ngrep":      {"binary": "ngrep",       "desc": "Network grep",          "flags": ["-d", "eth0", "-q"], "target_label": "Pattern", "timeout": 60},
        "iftop":      {"binary": "iftop",       "desc": "Bandwidth monitor",     "flags": ["-t", "-s", "5"], "target": False, "timeout": 30},
        "nethogs":    {"binary": "nethogs",     "desc": "Per-process bandwidth", "flags": ["-t", "-c", "3"], "target": False, "timeout": 30},
        "bmon":       {"binary": "bmon",        "desc": "Bandwidth monitor",     "flags": ["-o", "ascii", "-p", "eth0"], "target": False, "timeout": 10},
        "vnstat":     {"binary": "vnstat",      "desc": "Network statistics",    "flags": ["-h"], "target": False, "timeout": 10},
    },
    "Intrusion Detection": {
        "snort":      {"binary": "snort",       "desc": "IDS/IPS",               "flags": ["-T", "-c", "/etc/snort/snort.conf"], "target": False, "timeout": 30},
        "suricata":   {"binary": "suricata",    "desc": "IDS/IPS engine",        "flags": ["-T", "-c", "/etc/suricata/suricata.yaml"], "target": False, "timeout": 30},
        "zeek":       {"binary": "zeek",        "desc": "Network analysis",      "flags": ["-C", "-r"], "target_label": "PCAP file", "timeout": 120},
        "ossec":      {"binary": "ossec-control", "desc": "HIDS status",         "flags": ["status"], "target": False, "timeout": 10},
        "samhain":    {"binary": "samhain",     "desc": "File integrity HIDS",   "flags": ["-t", "init"], "target": False, "timeout": 120},
    },
    "Log Analysis": {
        "journalctl": {"binary": "journalctl",  "desc": "Systemd log viewer",    "handler": _journalctl_handler},
        "last":       {"binary": "last",        "desc": "Login history",         "flags": ["-n", "50"], "target": False, "timeout": 10},
        "lastb":      {"binary": "lastb",       "desc": "Failed login history",  "flags": ["-n", "50"], "target": False, "timeout": 10},
        "fail2ban":   {"binary": "fail2ban-client", "desc": "Ban status",        "flags": ["status"], "target": False, "timeout": 10},
        "logwatch":   {"binary": "logwatch",    "desc": "Log summarizer",        "handler": _logwatch_handler},
        "goaccess":   {"binary": "goaccess",    "desc": "Web log analyzer",      "flags": ["--log-format=COMBINED"], "target_label": "Access log", "timeout": 60},
        "grep-auth":  {"binary": "grep",        "desc": "Search auth logs",      "flags": ["-i", "failed", "/var/log/auth.log"], "target": False, "timeout": 10},
    },
    "Forensics & Malware": {
        "chkrootkit": {"binary": "chkrootkit",  "desc": "Rootkit detection",     "handler": _chkrootkit_handler},
        "rkhunter":   {"binary": "rkhunter",    "desc": "Rootkit hunter",        "handler": _rkhunter_handler},
        "lynis":      {"binary": "lynis",       "desc": "Security audit",        "handler": _lynis_handler},
        "clamscan":   {"binary": "clamscan",    "desc": "Antivirus scan",        "handler": _clamscan_handler},
        "yara":       {"binary": "yara",        "desc": "Pattern matching",      "handler": _yara_handler},
        "volatility3": {"binary": "vol3",       "desc": "Memory forensics",      "flags": ["-f"], "target_label": "Memory dump", "timeout": 300},
        "sleuthkit":  {"binary": "fls",         "desc": "Filesystem forensics",  "flags": ["-r"], "target_label": "Image file", "timeout": 120},
    },
    "Vulnerability Assessment": {
        "nmap-vuln":  {"binary": "nmap",        "desc": "Nmap vuln scripts",     "flags": ["--script", "vuln"], "timeout": 600},
        "nikto-blue": {"binary": "nikto",       "desc": "Web vuln scan",         "flags": ["-h"], "target_label": "URL", "timeout": 600},
        "testssl":    {"binary": "testssl.sh",  "desc": "TLS/SSL testing",       "flags": [], "target_label": "host:port", "timeout": 300},
        "ssh-audit":  {"binary": "ssh-audit",   "desc": "SSH config audit",      "flags": [], "target_label": "IP:port", "timeout": 30},
        "linpeas-blue": {"binary": "linpeas.sh", "desc": "Linux privesc audit",  "flags": [], "target": False, "timeout": 300},
        "unix-privesc": {"binary": "unix-privesc-check", "desc": "Privesc check", "flags": ["standard"], "target": False, "timeout": 120},
    },
    "System Hardening": {
        "iptables":   {"binary": "iptables",    "desc": "Firewall rules",        "handler": _iptables_handler},
        "nftables":   {"binary": "nft",         "desc": "Modern firewall",       "flags": ["list", "ruleset"], "target": False, "timeout": 10},
        "ufw":        {"binary": "ufw",         "desc": "Uncomplicated firewall", "flags": ["status", "verbose"], "target": False, "timeout": 10},
        "apparmor":   {"binary": "aa-status",   "desc": "AppArmor status",       "flags": [], "target": False, "timeout": 10},
        "aide":       {"binary": "aide",        "desc": "File integrity",        "handler": _aide_handler},
        "sestatus":   {"binary": "sestatus",    "desc": "SELinux status",        "flags": ["-v"], "target": False, "timeout": 10},
    },
    "Incident Response": {
        "dd":         {"binary": "dd",          "desc": "Disk imaging",          "handler": _dd_handler},
        "dc3dd":      {"binary": "dc3dd",       "desc": "Forensic disk copy",    "flags": [], "target_label": "if=/dev/sdX", "timeout": 3600},
        "lime":       {"binary": "insmod",      "desc": "LiME memory dump",      "flags": [], "target_label": "lime.ko path", "timeout": 120},
        "photorec":   {"binary": "photorec",    "desc": "File recovery",         "flags": [], "target_label": "Device/image", "timeout": 600},
        "ss":         {"binary": "ss",          "desc": "Active connections",    "flags": ["-tunap"], "target": False, "timeout": 10},
        "lsof":       {"binary": "lsof",        "desc": "Open files/processes",  "flags": ["-i"], "target": False, "timeout": 10},
    },
    "Threat Intelligence": {
        "whois":      {"binary": "whois",       "desc": "Domain lookup",         "flags": [], "target_label": "Domain/IP", "timeout": 30},
        "dig":        {"binary": "dig",         "desc": "DNS investigation",     "flags": ["ANY"], "target_label": "Domain", "timeout": 15},
        "nslookup":   {"binary": "nslookup",    "desc": "DNS query",             "flags": [], "target_label": "Domain", "timeout": 10},
        "traceroute": {"binary": "traceroute",  "desc": "Route tracing",         "flags": ["-n"], "target_label": "IP/host", "timeout": 60},
        "curl-headers": {"binary": "curl",      "desc": "HTTP header analysis",  "flags": ["-I", "-s"], "target_label": "URL", "timeout": 15},
        "nmap-os":    {"binary": "nmap",        "desc": "OS fingerprinting",     "flags": ["-O", "--osscan-guess"], "timeout": 120},
    },
}


def run(username: str, role: str):
    categories = list(BLUE_TOOLS.keys())
    while True:
        print("\n=== Blue Team Tools ===")
        for i, cat in enumerate(categories, 1):
            count = len(BLUE_TOOLS[cat])
            print(f"  {i}. {cat} ({count} tools)")
        print(f"  0. Back to Main Menu")
        choice = input("\nSelect category: ").strip()
        if choice == "0":
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(categories):
                _run_category(username, categories[idx])
            else:
                print("[!] Invalid.")
        except ValueError:
            print("[!] Enter a number.")


def _run_category(username: str, category: str):
    tools = BLUE_TOOLS[category]
    tool_names = list(tools.keys())
    while True:
        print(f"\n--- {category} ---")
        for i, name in enumerate(tool_names, 1):
            desc = tools[name].get("desc", "")
            binary = tools[name]["binary"]
            print(f"  {i:2}. {name:<20} {desc} [{binary}]")
        print(f"  0. Back")
        choice = input("\nSelect tool: ").strip()
        if choice == "0":
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(tool_names):
                name = tool_names[idx]
                print(f"\n{'='*50}")
                print(f"  Tool: {name}")
                print(f"  {tools[name].get('desc', '')}")
                print(f"{'='*50}")
                execute_tool(username, tools[name], "blue")
            else:
                print("[!] Invalid.")
        except ValueError:
            print("[!] Enter a number.")
