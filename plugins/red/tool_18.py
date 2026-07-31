import socket
import struct

NAME = "Packet Sniffer (basic)"
DESCRIPTION = "Capture and summarize packets on the LAN (root)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    raw = input("Packets to capture (default 20): ").strip()
    count = int(raw) if raw.isdigit() else 20

    try:
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    except PermissionError:
        print("[!] Raw sockets require root.")
        return

    print(f"[*] Capturing {count} packets (Ctrl+C to stop)...")
    captured = 0
    try:
        while captured < count:
            pkt, _ = s.recvfrom(65535)
            proto = struct.unpack("!H", pkt[12:14])[0]

            if proto == 0x0800:  # IPv4
                src = socket.inet_ntoa(pkt[26:30])
                dst = socket.inet_ntoa(pkt[30:34])
                ip_proto = pkt[23]
                name = {1: "ICMP", 6: "TCP", 17: "UDP"}.get(ip_proto, str(ip_proto))
                print(f"  IPv4 {name:<5} {src:<15} -> {dst}")
            elif proto == 0x0806:
                print("  ARP  frame")
            elif proto == 0x86DD:
                print("  IPv6 frame")
            else:
                print(f"  EtherType 0x{proto:04x}")
            captured += 1
    except KeyboardInterrupt:
        print("\n[!] Capture stopped.")
    finally:
        s.close()
    print(f"[+] {captured} packet(s) captured.")
