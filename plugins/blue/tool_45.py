import subprocess
from pathlib import Path

NAME = "DNS Configuration Auditor"
DESCRIPTION = "Review resolv.conf and test DNS resolution health."
ALLOWED_ROLES = ["admin", "instructor", "student"]

RESOLV = Path("/etc/resolv.conf")
TEST_DOMAINS = ["google.com", "github.com", "cloudflare.com"]


def run(username, role):
    print("=== DNS Configuration ===\n")

    if RESOLV.exists():
        content = RESOLV.read_text(errors="ignore")
        nameservers = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                print(f"  {stripped}")
                if stripped.startswith("nameserver"):
                    nameservers.append(stripped.split()[1])

        if not nameservers:
            print("  [!] No nameserver entries found.")
    else:
        print("  [!] /etc/resolv.conf does not exist.")
        nameservers = []

    # systemd-resolved check
    resolved = subprocess.run(
        ["systemctl", "is-active", "systemd-resolved"],
        capture_output=True, text=True, timeout=5,
    )
    if resolved.stdout.strip() == "active":
        print("\n  [i] systemd-resolved is active.")
        result = subprocess.run(
            ["resolvectl", "status"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines()[:15]:
                print(f"    {line}")

    # Resolution tests
    print("\n--- Resolution Tests ---")
    import socket
    for domain in TEST_DOMAINS:
        try:
            ip = socket.gethostbyname(domain)
            print(f"  [+] {domain:<20} -> {ip}")
        except socket.gaierror as e:
            print(f"  [!] {domain:<20} FAILED: {e}")

    # DNSSEC check (if dig available)
    try:
        result = subprocess.run(
            ["dig", "+dnssec", "cloudflare.com", "A", "+short"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"\n  [i] DNSSEC test (cloudflare.com): {result.stdout.strip()}")
    except FileNotFoundError:
        pass
