import socket
import logging
from datetime import datetime
from pathlib import Path

NAME = "Low-Interaction Honeypot"
DESCRIPTION = "Listen on a port and log connection attempts."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/blue/reports")
log = logging.getLogger("cyberlab.blue.honeypot")

BANNERS = {
    "ssh":  b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3\r\n",
    "ftp":  b"220 (vsFTPd 3.0.5)\r\n",
    "smtp": b"220 mail.lab.local ESMTP Postfix\r\n",
    "http": b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.54\r\n\r\n",
}


def run(username, role):
    raw_port = input("Port to listen on (default 2222): ").strip()
    port = int(raw_port) if raw_port.isdigit() else 2222

    print("Banner type:")
    for i, name in enumerate(BANNERS, 1):
        print(f"  {i}. {name}")
    banner_choice = input("Select [1]: ").strip() or "1"
    banner_key = list(BANNERS.keys())[int(banner_choice) - 1
                                       if banner_choice.isdigit()
                                       and 1 <= int(banner_choice) <= len(BANNERS)
                                       else 0]
    banner = BANNERS[banner_key]

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", port))
        server.listen(5)
        print(f"[*] Honeypot ACTIVE on port {port} ({banner_key} banner)")
        print("[*] Press Ctrl+C to stop.\n")
    except OSError as e:
        print(f"[!] Bind failed: {e}")
        return

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    log_file = REPORT_DIR / "honeypot_log.txt"
    events = 0

    try:
        while True:
            client, addr = server.accept()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            events += 1

            entry = f"[{timestamp}] Connection from {addr[0]}:{addr[1]}"
            print(f"\a[!] ALERT #{events}: {entry}")

            payload = b""
            try:
                client.sendall(banner)
                client.settimeout(3)
                payload = client.recv(1024)
                if payload:
                    decoded = payload.decode(errors="ignore").strip()
                    entry += f" | payload: {decoded[:200]}"
                    print(f"    Received: {decoded[:100]}")
            except socket.timeout:
                pass
            except OSError:
                pass
            finally:
                client.close()

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(entry + "\n")

    except KeyboardInterrupt:
        print(f"\n[*] Honeypot stopped. {events} event(s) logged to {log_file}")
    finally:
        server.close()
