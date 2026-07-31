import socket

NAME = "DNS Recon"
DESCRIPTION = "Resolve a domain and enumerate common sub-hosts."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    target = input("Target domain (e.g. example.com): ").strip()
    if not target:
        return

    try:
        ip = socket.gethostbyname(target)
        print(f"[+] {target} -> {ip}")
        try:
            print(f"[+] Reverse: {socket.gethostbyaddr(ip)[0]}")
        except socket.herror:
            pass
    except socket.gaierror as e:
        print(f"[!] Lookup failed: {e}")
        return

    print("\n[*] Checking common host records...")
    for prefix in ["www", "mail", "ns1", "ns2", "ftp", "admin",
                   "dev", "test", "vpn", "api"]:
        host = f"{prefix}.{target}"
        try:
            print(f"  [+] {host:<22} -> {socket.gethostbyname(host)}")
        except socket.gaierror:
            pass
