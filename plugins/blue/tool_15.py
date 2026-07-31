import shutil

NAME = "IDS Status Check"
DESCRIPTION = "Verify Snort/Suricata/Zeek installation and status."
ALLOWED_ROLES = ["admin", "instructor", "student"]

IDS_LIST = [
    ("suricata", ["suricata", "--build-info"]),
    ("snort", ["snort", "-V"]),
    ("zeek", ["zeek", "--version"]),
]


def run(username, role):
    print("=== IDS/IPS Status ===")
    for name, _ in IDS_LIST:
        binary = IDS_LIST[0][0] if name == "suricata" else (
            "snort" if name == "snort" else "zeek")
        if not shutil.which(binary):
            print(f"\n[-] {name:<10} NOT installed")
            continue

        cmd = [binary, "--version"]
        if name == "snort":
            cmd = [binary, "-V"]
        if name == "zeek":
            cmd = [binary, "--version"]
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        out = (result.stdout or result.stderr).strip().splitlines()
        print(f"\n[+] {name:<10} INSTALLED")
        for line in out[:2]:
            print(f"    {line.strip()}")

    print("\n[*] To start services: systemctl start suricata / snort / zeek")
