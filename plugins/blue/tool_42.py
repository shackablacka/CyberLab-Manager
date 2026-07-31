import subprocess
from pathlib import Path
from core.tool_runner import run_tool, is_installed

NAME = "Traffic Capture Analyzer"
DESCRIPTION = "Capture or read pcap traffic with tcpdump/tshark."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/blue/reports")


def run(username, role):
    print("1. Live capture (tcpdump)")
    print("2. Read existing pcap file")
    choice = input("Select: ").strip()

    if choice == "1":
        live_capture()
    elif choice == "2":
        read_pcap()
    else:
        print("[!] Invalid choice.")


def live_capture():
    iface = input("Interface (default eth0): ").strip() or "eth0"
    raw_count = input("Packet count (default 50): ").strip()
    count = raw_count if raw_count.isdigit() else "50"

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    pcap_out = REPORT_DIR / "capture.pcap"

    print(f"[*] Capturing {count} packets on {iface}...")
    print("[*] Press Ctrl+C to stop early.\n")

    run_tool(
        "tcpdump",
        ["-i", iface, "-c", count, "-w", str(pcap_out), "-v"],
        package="tcpdump",
    )
    print(f"\n[+] Capture saved: {pcap_out}")
    print(f"[*] Analyze with: tcpdump -r {pcap_out} -nn")


def read_pcap():
    path = input("Path to pcap file: ").strip()
    if not Path(path).is_file():
        print("[!] File not found.")
        return

    if is_installed("tshark"):
        print("[*] Analyzing with tshark...\n")
        subprocess.run(
            ["tshark", "-r", path, "-c", "50", "-q", "-z", "conv,ip"],
            check=False,
        )
    elif is_installed("tcpdump"):
        print("[*] Reading with tcpdump...\n")
        subprocess.run(
            ["tcpdump", "-r", path, "-nn", "-c", "50"],
            check=False,
        )
    else:
        print("[!] Install tcpdump or tshark to read pcap files.")
