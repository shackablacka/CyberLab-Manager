import socket

NAME = "SSH Version Auditor"
DESCRIPTION = "Grab SSH banners and flag outdated/vulnerable versions."
ALLOWED_ROLES = ["admin", "instructor", "student"]

VULNERABLE = {
    "openssh_4.": "Very old — many known CVEs",
    "openssh_5.": "Old — user enumeration (CVE-2018-15473) likely",
    "openssh_6.": "Old — user enumeration (CVE-2018-15473) likely",
    "openssh_7.2": "Check CVE-2016-0777 (roaming)",
    "openssh_8.5": "Check for vendor backport status",
    "openssh_9.3": "Terrapin attack (CVE-2023-48795) if unpatched",
}


def run(username, role):
    targets = input("Target IP(s), comma-separated: ").strip()
    if not targets:
        return

    for target in [t.strip() for t in targets.split(",")]:
        try:
            s = socket.create_connection((target, 22), timeout=4)
            banner = s.recv(200).decode(errors="ignore").strip()
            s.close()
            print(f"\n[+] {target}: {banner}")

            low = banner.lower()
            for prefix, note in VULNERABLE.items():
                if prefix in low:
                    print(f"    [!] {note}")
                    break
            else:
                print("    [i] No flagged version — verify patch level manually.")
        except (OSError, socket.timeout):
            print(f"[-] {target}: port 22 closed/filtered")
