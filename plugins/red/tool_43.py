import socket
import struct
import time

NAME = "Traceroute Mapper"
DESCRIPTION = "Map the network path to a lab host (ICMP TTL method)."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    target = input("Target host/IP: ").strip()
    if not target:
        return

    try:
        dest = socket.gethostbyname(target)
    except socket.gaierror:
        print("[!] Could not resolve host.")
        return

    print(f"[*] Tracing route to {target} ({dest}), max 20 hops...")
    try:
        recv = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        recv.settimeout(2)
    except PermissionError:
        print("[!] Raw sockets require root.")
        return

    for ttl in range(1, 21):
        send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        send.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        start = time.time()
        send.sendto(b"cyberlab", (dest, 33434))

        try:
            _, addr = recv.recvfrom(512)
            rtt = (time.time() - start) * 1000
            try:
                name = socket.gethostbyaddr(addr[0])[0]
            except socket.herror:
                name = addr[0]
            print(f"  {ttl:2d}  {name:<30} {addr[0]:<15} {rtt:6.1f} ms")
            send.close()
            if addr[0] == dest:
                print("[+] Reached destination.")
                break
        except socket.timeout:
            print(f"  {ttl:2d}  * (no reply)")
            send.close()

    recv.close()
