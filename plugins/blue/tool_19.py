import subprocess
from collections import Counter

NAME = "Open Port Service Mapper"
DESCRIPTION = "List open ports with services and count exposure states."
ALLOWED_ROLES = ["admin", "instructor", "student"]

COMMON_PORTS = {20, 21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445,
                993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 8080}


def run(username, role):
    # Get listening ports
    for cmd, args in (("ss", ["-tlnp"]), ("netstat", ["-tlnp"])):
        try:
            result = subprocess.run([cmd] + args, capture_output=True,
                                    text=True, timeout=10)
            if result.returncode == 0:
                break
        except FileNotFoundError:
            continue
    else:
        print("[!] No connection diagnostics tools found.")
        return

    lines = result.stdout.splitlines()[1:]
    ports = []
    services = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            address = parts[3]
            if address.startswith("[::]") or address.startswith("0.0.0.0"):
                port = int(address.rsplit(":", 1)[-1])
                ports.append(port)
                service = parts[-1] if parts[-1] != "-" and "users" not in parts[-1] else "?"
                services.append(service)

    print(f"\n[+] {len(ports)} listening TCP port(s).\n")
    print("--- Listening Ports ---")
    port_counter = Counter(ports)
    for port, count in port_counter.most_common():
        common = " (common)" if port in COMMON_PORTS else " (uncommon)"
        print(f"  {port:<7} {count} listener{'' if count==1 else 's'}{common}")

    print("\n--- Exposed on all interfaces ---")
    for line in lines:
        parts = line.split()
        addr = parts[3] if len(parts) > 3 else ""
        if addr.startswith("0.0.0.0") or addr.startswith("[::]"):
            print(f"  {line.strip()}")
