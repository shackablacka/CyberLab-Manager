import subprocess

NAME = "Ping Sweep"
DESCRIPTION = "Discover live hosts in a /24 lab subnet."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    base = input("Subnet base (e.g. 192.168.1): ").strip()
    if base.count(".") != 2:
        print("[!] Expected format: X.X.X")
        return

    live = []
    print(f"[*] Sweeping {base}.0/24 ...")
    for host in range(1, 255):
        ip = f"{base}.{host}"
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            print(f"  [+] {ip} is up")
            live.append(ip)

    print(f"\n[+] {len(live)} host(s) responding.")
