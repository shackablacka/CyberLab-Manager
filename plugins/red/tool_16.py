import socket
import ssl
from datetime import datetime

NAME = "SSL Certificate Inspector"
DESCRIPTION = "Inspect a lab host's TLS certificate and cipher."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    host = input("Host (e.g. example.com): ").strip()
    if not host:
        return
    port = input("Port (default 443): ").strip() or "443"

    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, int(port)), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                print(f"\n  TLS version : {ssock.version()}")
                print(f"  Cipher      : {ssock.cipher()[0]}")
                subject = dict(x[0] for x in cert.get("subject", []))
                issuer = dict(x[0] for x in cert.get("issuer", []))
                print(f"  Subject CN  : {subject.get('commonName', '?')}")
                print(f"  Issuer      : {issuer.get('organizationName', '?')}")
                expires = datetime.strptime(
                    cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                )
                days = (expires - datetime.utcnow()).days
                print(f"  Valid until : {cert['notAfter']} ({days} days left)")
                if days < 30:
                    print("  [!] Certificate expires soon!")
    except ssl.SSLError as e:
        print(f"[!] TLS error: {e}")
    except (OSError, ValueError) as e:
        print(f"[!] Connection failed: {e}")
