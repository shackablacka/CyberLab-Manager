import socket

NAME = "Banner Grabber"
DESCRIPTION = "Grab service banners from open TCP ports."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    target = input("Target IP/host (lab only): ").strip()
    if not target:
        return
    raw = input("Ports (comma-separated, blank = common): ").strip()
    ports = ([int(p) for p in raw.split(",") if p.strip().isdigit()]
             if raw else [21, 22, 25, 80, 110, 143, 443])

    for port in ports:
        try:
            s = socket.create_connection((target, port), timeout=2)
            if port in (80, 443):
                s.sendall(b"HEAD / HTTP/1.0\r\nHost: x\r\n\r\n")
            banner = s.recv(200).decode(errors="ignore").strip()
            s.close()
            if banner:
                first = banner.splitlines()[0] if banner else ""
                print(f"  [+] {port:<6} {first[:80]}")
            else:
                print(f"  [-] {port:<6} (no banner)")
        except (OSError, socket.timeout):
            print(f"  [-] {port:<6} closed/filtered")
