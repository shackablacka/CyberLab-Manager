"""Red Team module - 50 offensive security tools from Kali."""

import logging
from modules.tool_runner import execute_tool, sanitize, get_user_id, \
    check_tool, run_command, save_scan

log = logging.getLogger("cyberlab.redteam")


def _hydra_handler(username, tool_def, team):
    target = sanitize(input("Target IP: ").strip())
    if not target:
        return
    print("\nProtocols: ssh ftp http-post-form smb rdp mysql mssql")
    proto = sanitize(input("Protocol: ").strip()) or "ssh"
    users = input("User list [/usr/share/wordlists/metasploit/unix_users.txt]: ").strip() \
        or "/usr/share/wordlists/metasploit/unix_users.txt"
    passes = input("Pass list [/usr/share/wordlists/rockyou.txt]: ").strip() \
        or "/usr/share/wordlists/rockyou.txt"
    cmd = ["hydra", "-L", users, "-P", passes, "-t", "4", target, proto]
    print(f"\n[*] Running: hydra -L ... -P ... {target} {proto}")
    uid = get_user_id(username)
    out, rc = run_command(cmd, 900)
    save_scan(uid, "hydra", target, proto, out, "completed" if rc == 0 else "failed", team)
    print(out[:3000])


def _sqlmap_handler(username, tool_def, team):
    target = sanitize(input("Target URL (e.g. http://x.com/page?id=1): ").strip())
    if not target:
        return
    print("\n1. Basic test  2. Full test  3. Enumerate DBs  4. Custom")
    c = input("Select: ").strip()
    flags = {
        "1": ["--batch", "--level=1"],
        "2": ["--batch", "--level=5", "--risk=3", "--tamper=space2comment"],
        "3": ["--batch", "--dbs"],
    }.get(c, ["--batch"])
    if c == "4":
        extra = sanitize(input("Flags: ").strip()) or ""
        flags = extra.split()
    cmd = ["sqlmap", "-u", target] + flags
    print(f"\n[*] Running: sqlmap -u {target} ...")
    uid = get_user_id(username)
    out, rc = run_command(cmd, 600)
    save_scan(uid, "sqlmap", target, " ".join(flags), out, "completed" if rc == 0 else "failed", team)
    print(out[:3000])


def _msfconsole_handler(username, tool_def, team):
    print("\n[*] Launching msfconsole in non-interactive mode.")
    resource = sanitize(input("Resource file (or Enter for version check): ").strip())
    uid = get_user_id(username)
    if resource:
        cmd = ["msfconsole", "-q", "-r", resource]
    else:
        print("[!] Use msfconsole directly for interactive sessions.")
        print("[*] Running: msfconsole -q -x 'version; exit'")
        cmd = ["msfconsole", "-q", "-x", "version; exit"]
    out, rc = run_command(cmd, 60)
    save_scan(uid, "metasploit", resource or "interactive", "", out, "completed", team)
    print(out[:2000])


def _john_handler(username, tool_def, team):
    print("\n1. Crack /etc/shadow  2. Custom hash file  3. Wordlist mode")
    c = input("Select: ").strip()
    uid = get_user_id(username)
    if c == "1":
        cmd = ["john", "--wordlist=/usr/share/wordlists/rockyou.txt", "/etc/shadow"]
    elif c == "2":
        f = sanitize(input("Hash file path: ").strip())
        if not f:
            return
        cmd = ["john", "--wordlist=/usr/share/wordlists/rockyou.txt", f]
    elif c == "3":
        f = sanitize(input("Hash file: ").strip())
        wl = sanitize(input("Wordlist: ").strip()) or "/usr/share/wordlists/rockyou.txt"
        if not f:
            return
        cmd = ["john", f"--wordlist={wl}", f]
    else:
        return
    out, rc = run_command(cmd, 600)
    save_scan(uid, "john", c, "", out, "completed" if rc == 0 else "failed", team)
    print(out[:3000])


def _hashcat_handler(username, tool_def, team):
    f = sanitize(input("Hash file: ").strip())
    if not f:
        return
    print("\nHash types: 0=MD5 100=SHA1 1000=NTLM 1800=sha512crypt 3200=bcrypt")
    ht = sanitize(input("Hash type [1000]: ").strip()) or "1000"
    wl = sanitize(input("Wordlist [/usr/share/wordlists/rockyou.txt]: ").strip()) \
        or "/usr/share/wordlists/rockyou.txt"
    cmd = ["hashcat", "-m", ht, f, wl, "--force"]
    uid = get_user_id(username)
    out, rc = run_command(cmd, 900)
    save_scan(uid, "hashcat", f, f"-m {ht}", out, "completed" if rc == 0 else "failed", team)
    print(out[:3000])


def _aircrack_handler(username, tool_def, team):
    cap = sanitize(input("Capture file (.cap): ").strip())
    if not cap:
        return
    wl = sanitize(input("Wordlist [/usr/share/wordlists/rockyou.txt]: ").strip()) \
        or "/usr/share/wordlists/rockyou.txt"
    cmd = ["aircrack-ng", cap, "-w", wl]
    uid = get_user_id(username)
    out, rc = run_command(cmd, 600)
    save_scan(uid, "aircrack-ng", cap, "", out, "completed" if rc == 0 else "failed", team)
    print(out[:3000])


RED_TOOLS = {
    "Reconnaissance": {
        "nmap":       {"binary": "nmap",       "desc": "Port scanner",          "flags": ["-sC", "-sV"], "timeout": 600},
        "masscan":    {"binary": "masscan",     "desc": "Mass IP port scanner",  "flags": ["-p1-65535", "--rate=1000"], "timeout": 300},
        "dmitry":     {"binary": "dmitry",      "desc": "Deepmagic info gather", "flags": ["-winse"], "timeout": 120},
        "fierce":     {"binary": "fierce",      "desc": "DNS reconnaissance",    "flags": ["--domain"], "target_label": "Domain", "timeout": 120},
        "dnsenum":    {"binary": "dnsenum",     "desc": "DNS enumeration",       "flags": [], "target_label": "Domain", "timeout": 120},
        "theHarvester": {"binary": "theHarvester", "desc": "Email/domain recon", "flags": ["-d"], "target_label": "Domain", "timeout": 120},
        "recon-ng":   {"binary": "recon-ng",    "desc": "OSINT framework",       "flags": [], "target": False, "timeout": 60},
    },
    "Scanning & Enumeration": {
        "nikto":      {"binary": "nikto",       "desc": "Web server scanner",    "flags": ["-h"], "target_label": "URL", "timeout": 600},
        "gobuster":   {"binary": "gobuster",    "desc": "Directory brute force", "flags": ["dir", "-u"], "target_label": "URL", "timeout": 600},
        "dirb":       {"binary": "dirb",        "desc": "Web content scanner",   "flags": [], "target_label": "URL", "timeout": 600},
        "enum4linux": {"binary": "enum4linux",  "desc": "SMB enumeration",       "flags": ["-a"], "timeout": 300},
        "smbclient":  {"binary": "smbclient",   "desc": "SMB client",            "flags": ["-L"], "target_label": "//IP", "timeout": 60},
        "snmpwalk":   {"binary": "snmpwalk",    "desc": "SNMP enumeration",      "flags": ["-v2c", "-c", "public"], "timeout": 120},
        "onesixtyone": {"binary": "onesixtyone", "desc": "SNMP scanner",         "flags": ["-c", "/usr/share/seclists/Discovery/SNMP/snmp.txt"], "timeout": 60},
    },
    "Web Application": {
        "sqlmap":     {"binary": "sqlmap",      "desc": "SQL injection",         "handler": _sqlmap_handler},
        "wpscan":     {"binary": "wpscan",      "desc": "WordPress scanner",     "flags": ["--url"], "target_label": "URL", "timeout": 300},
        "whatweb":    {"binary": "whatweb",     "desc": "Web fingerprinting",    "flags": ["-a", "3"], "target_label": "URL", "timeout": 60},
        "wfuzz":      {"binary": "wfuzz",       "desc": "Web fuzzer",            "flags": ["-c", "-z", "file,/usr/share/wordlists/dirb/common.txt", "--hc", "404"], "target_label": "URL (FUZZ)", "timeout": 300},
        "ffuf":       {"binary": "ffuf",        "desc": "Fast web fuzzer",       "flags": ["-w", "/usr/share/wordlists/dirb/common.txt", "-u"], "target_label": "URL/FUZZ", "timeout": 300},
        "commix":     {"binary": "commix",      "desc": "Command injection",     "flags": ["--batch", "-u"], "target_label": "URL", "timeout": 300},
        "dalfox":     {"binary": "dalfox",      "desc": "XSS scanner",           "flags": ["url"], "target_label": "URL", "timeout": 300},
    },
    "Password Attacks": {
        "hydra":      {"binary": "hydra",       "desc": "Online brute force",    "handler": _hydra_handler},
        "john":       {"binary": "john",        "desc": "Password cracker",      "handler": _john_handler},
        "hashcat":    {"binary": "hashcat",     "desc": "GPU password cracker",  "handler": _hashcat_handler},
        "crunch":     {"binary": "crunch",      "desc": "Wordlist generator",    "flags": ["8", "12", "abcdefghijklmnopqrstuvwxyz0123456789", "-o", "wordlist.txt"], "target": False, "timeout": 120},
        "cewl":       {"binary": "cewl",        "desc": "Custom wordlist from site", "flags": ["-d", "2", "-m", "5", "-w", "cewl.txt"], "target_label": "URL", "timeout": 120},
        "medusa":     {"binary": "medusa",      "desc": "Parallel brute force",  "flags": ["-h"], "timeout": 600},
    },
    "Exploitation": {
        "msfconsole": {"binary": "msfconsole",  "desc": "Metasploit framework",  "handler": _msfconsole_handler},
        "searchsploit": {"binary": "searchsploit", "desc": "Exploit DB search",  "flags": [], "target_label": "Search term", "timeout": 30},
        "setoolkit":  {"binary": "setoolkit",   "desc": "Social engineering",    "flags": [], "target": False, "timeout": 60},
        "beef-xss":   {"binary": "beef-xss",    "desc": "Browser exploitation",  "flags": [], "target": False, "timeout": 30},
        "impacket-psexec": {"binary": "impacket-psexec", "desc": "Remote exec via SMB", "flags": [], "target_label": "domain/user:pass@IP", "timeout": 60},
        "evil-winrm": {"binary": "evil-winrm",  "desc": "WinRM shell",           "flags": ["-i"], "target_label": "IP", "timeout": 60},
    },
    "Post-Exploitation": {
        "impacket-smbexec": {"binary": "impacket-smbexec", "desc": "SMB remote exec", "flags": [], "target_label": "domain/user:pass@IP", "timeout": 60},
        "impacket-wmiexec": {"binary": "impacket-wmiexec", "desc": "WMI remote exec", "flags": [], "target_label": "domain/user:pass@IP", "timeout": 60},
        "impacket-secretsdump": {"binary": "impacket-secretsdump", "desc": "Dump hashes", "flags": [], "target_label": "domain/user:pass@IP", "timeout": 120},
        "linpeas":    {"binary": "linpeas.sh",  "desc": "Linux privesc checker", "flags": [], "target": False, "timeout": 300},
        "pspy":       {"binary": "pspy64",      "desc": "Process monitor (privesc)", "flags": [], "target": False, "timeout": 60},
    },
    "Sniffing & MITM": {
        "tshark":     {"binary": "tshark",      "desc": "Packet analysis (CLI)", "flags": ["-i", "eth0", "-c", "100"], "target": False, "timeout": 120},
        "tcpdump":    {"binary": "tcpdump",     "desc": "Packet capture",        "flags": ["-i", "eth0", "-c", "50", "-nn"], "target": False, "timeout": 120},
        "ettercap":   {"binary": "ettercap",    "desc": "MITM attack",           "flags": ["-T", "-q", "-i", "eth0"], "target": False, "timeout": 60},
        "responder":  {"binary": "responder",   "desc": "LLMNR/NBT-NS poisoner", "flags": ["-I", "eth0", "-v"], "target": False, "timeout": 120},
        "mitmproxy":  {"binary": "mitmproxy",   "desc": "HTTP/HTTPS proxy",      "flags": ["--mode", "regular", "-p", "8080"], "target": False, "timeout": 60},
        "dsniff":     {"binary": "dsniff",      "desc": "Network credential sniffer", "flags": ["-i", "eth0"], "target": False, "timeout": 60},
    },
    "Wireless": {
        "aircrack-ng": {"binary": "aircrack-ng", "desc": "WiFi key cracker",    "handler": _aircrack_handler},
        "airmon-ng":  {"binary": "airmon-ng",   "desc": "Monitor mode toggle",  "flags": ["start"], "target_label": "Interface", "timeout": 30},
        "airodump-ng": {"binary": "airodump-ng", "desc": "WiFi packet capture", "flags": [], "target_label": "Interface", "timeout": 60},
        "wifite":     {"binary": "wifite",      "desc": "Automated WiFi audit", "flags": ["--kill"], "target": False, "timeout": 300},
    },
    "Reverse Engineering": {
        "radare2":    {"binary": "r2",          "desc": "Reverse engineering",   "flags": ["-A"], "target_label": "Binary path", "timeout": 60},
        "strings":    {"binary": "strings",     "desc": "Extract strings",       "flags": ["-n", "8"], "target_label": "File path", "timeout": 30},
        "binwalk":    {"binary": "binwalk",     "desc": "Firmware analysis",     "flags": ["-e"], "target_label": "File path", "timeout": 120},
    },
}


def run(username: str, role: str):
    categories = list(RED_TOOLS.keys())
    while True:
        print("\n=== Red Team Tools ===")
        for i, cat in enumerate(categories, 1):
            count = len(RED_TOOLS[cat])
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
    tools = RED_TOOLS[category]
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
                execute_tool(username, tools[name], "red")
            else:
                print("[!] Invalid.")
        except ValueError:
            print("[!] Enter a number.")
