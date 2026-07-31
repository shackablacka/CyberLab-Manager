import socket
from pathlib import Path

NAME = "Subdomain Enumerator"
DESCRIPTION = "Brute-force subdomains from a wordlist."
ALLOWED_ROLES = ["admin", "instructor"]

DEFAULT_WORDS = ["www", "mail", "ftp", "dev", "test", "staging",
                 "api", "admin", "vpn", "portal", "blog", "shop"]


def run(username, role):
    domain = input("Target domain: ").strip()
    if not domain:
        return

    wordlist = input("Wordlist path (blank = built-in): ").strip()
    if wordlist and Path(wordlist).is_file():
        words = Path(wordlist).read_text(encoding="utf-8").split()
    else:
        words = DEFAULT_WORDS

    found = 0
    for word in words:
        host = f"{word}.{domain}"
        try:
            ip = socket.gethostbyname(host)
            print(f"  [+] {host:<30} -> {ip}")
            found += 1
        except socket.gaierror:
            pass
    print(f"\n[+] {found} subdomain(s) resolved.")
