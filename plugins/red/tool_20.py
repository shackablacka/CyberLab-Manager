import socket

NAME = "Catch Listener"
DESCRIPTION = "netcat-style listener for lab reverse shells."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    raw = input("Listen port (default 4444): ").strip()
    port = int(raw) if raw.isdigit() else 4444

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", port))
        server.listen(1)
        print(f"[*] Listening on 0.0.0.0:{port} (Ctrl+C to stop)...")
        conn, addr = server.accept()
        print(f"[+] Connection from {addr[0]}:{addr[1]}")
        print("[*] Type commands ('exit' to close):\n")

        conn.settimeout(0.5)
        while True:
            cmd = input("shell> ").strip()
            if cmd in ("exit", "quit"):
                break
            if not cmd:
                continue
            conn.sendall((cmd + "\n").encode())
            output = b""
            while True:
                try:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    output += chunk
                except socket.timeout:
                    break
            print(output.decode(errors="ignore"), end="")
        conn.close()
    except KeyboardInterrupt:
        print("\n[!] Listener stopped.")
    except OSError as e:
        print(f"[!] Bind failed: {e}")
    finally:
        server.close()
