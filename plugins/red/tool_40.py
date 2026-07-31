import socket
import threading
from pathlib import Path

NAME = "File Transfer (nc-style)"
DESCRIPTION = "Send/receive files over raw TCP in the lab."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("1. Receive a file (listen)")
    print("2. Send a file (connect)")
    choice = input("Select: ").strip()

    if choice == "1":
        receive_file()
    elif choice == "2":
        send_file()
    else:
        print("[!] Invalid choice.")


def receive_file():
    raw = input("Listen port (default 9000): ").strip()
    port = int(raw) if raw.isdigit() else 9000
    out = Path(input("Save as (default received.bin): ").strip()
               or "received.bin")

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", port))
        server.listen(1)
        print(f"[*] Listening on 0.0.0.0:{port} ...")
        conn, addr = server.accept()
        print(f"[+] Connection from {addr[0]}:{addr[1]}")

        received = 0
        with open(out, "wb") as f:
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
        conn.close()
        print(f"[+] Received {received} bytes -> {out}")
    except OSError as e:
        print(f"[!] Failed: {e}")
    finally:
        server.close()


def send_file():
    host = input("Receiver IP: ").strip()
    raw = input("Port (default 9000): ").strip()
    port = int(raw) if raw.isdigit() else 9000
    path = Path(input("File to send: ").strip())

    if not host or not path.is_file():
        print("[!] Host and valid file required.")
        return

    size = path.stat().st_size
    try:
        with socket.create_connection((host, port), timeout=10) as s:
            print(f"[*] Sending {path.name} ({size} bytes)...")
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    s.sendall(chunk)
        print("[+] Transfer complete.")
    except OSError as e:
        print(f"[!] Failed: {e}")
