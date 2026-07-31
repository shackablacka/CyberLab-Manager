import socket
from pathlib import Path
from core.tool_runner import is_installed, run_tool

NAME = "Port Scanner"
DESCRIPTION = "Scan a target for open TCP ports (nmap or native)."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/red/reports")


def run(username, role):
    target = input("Target IP/host (lab only): ").strip()
    if not target:
        return

    if is_installed("nmap"):
        run_tool("nmap", ["-F", target])
        return

    print("[*] nmap not found, using native scanner.")
    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        print("[!] Could not resolve host.")
        return

    ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445,
             3306, 3389, 5432, 5900, 8080, 8443]
    results = [f"Native port scan of {target} ({ip})"]
    for port in ports:
        s = socket.socket()
        s.settimeout(0.5)
        if s.connect_ex((ip, port)) == 0:
            line = f"  {port:<6} OPEN"
            print(line)
            results.append(line)
        s.close()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"portscan_{ip.replace('.', '_')}.txt"
    out.write_text("\n".join(results), encoding="utf-8")
    print(f"[+] Report saved: {out}")
