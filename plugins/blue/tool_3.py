import subprocess

NAME = "Listening Port Auditor"
DESCRIPTION = "List listening sockets with owning processes."
ALLOWED_ROLES = ["admin", "instructor", "student"]

KNOWN_SERVICES = {22, 53, 80, 443, 3306, 5432}


def run(username, role):
    print("[*] Enumerating listening sockets...\n")

    if _try("ss", ["-tlnp"]) or _try("netstat", ["-tlnp"]):
        pass
    else:
        _native_proc_net()

    print("\n[*] Review: any port you can't justify is an investigation lead.")
    print("[*] Known service ports: " +
          ", ".join(str(p) for p in sorted(KNOWN_SERVICES)))


def _try(cmd, args):
    try:
        result = subprocess.run([cmd] + args, capture_output=True,
                                text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print(result.stdout)
            return True
    except FileNotFoundError:
        pass
    return False


def _native_proc_net():
    print(f"{'Proto':<6}{'Local Address':<24}{'State'}")
    for proto, path in (("tcp", "/proc/net/tcp"), ("tcp6", "/proc/net/tcp6"),
                        ("udp", "/proc/net/udp")):
        try:
            lines = Path(path).read_text().splitlines()[1:]
        except FileNotFoundError:
            continue
        for line in lines:
            parts = line.split()
            local, state = parts[1], parts[3]
            if state != "0A" and proto.startswith("tcp"):
                continue  # 0A = LISTEN
            ip_hex, port_hex = local.rsplit(":", 1)
            port = int(port_hex, 16)
            print(f"{proto:<6}*:{port:<20}{'LISTEN' if state == '0A' else 'UDP'}")
