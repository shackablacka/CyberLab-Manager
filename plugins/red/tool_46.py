import subprocess

NAME = "SUID/SGID Finder"
DESCRIPTION = "Find SUID/SGID binaries and flag known-abusable ones."
ALLOWED_ROLES = ["admin", "instructor", "student"]

GTFOBINS = {"nmap", "vim", "vi", "find", "bash", "sh", "python", "python3",
            "perl", "ruby", "less", "more", "awk", "man", "tar", "cp",
            "nano", "env", "ftp", "gdb", "php", "node"}


def run(username, role):
    print("[*] Searching for SUID/SGID binaries (this takes a moment)...")
    result = subprocess.run(
        ["bash", "-c", "find / -type f \\( -perm -4000 -o -perm -2000 \\) 2>/dev/null"],
        capture_output=True, text=True, timeout=120,
    )
    files = result.stdout.strip().splitlines()
    print(f"\n[+] {len(files)} SUID/SGID file(s) found.\n")

    interesting = []
    for f in files:
        name = f.rsplit("/", 1)[-1]
        if name in GTFOBINS:
            interesting.append(f)

    if interesting:
        print("[!] Potentially abusable (check GTFOBins):")
        for f in interesting:
            print(f"    {f}")
    else:
        print("[+] No well-known GTFOBins candidates found.")

    print("\nAll findings:")
    for f in files[:40]:
        print(f"    {f}")
    if len(files) > 40:
        print(f"    ... and {len(files) - 40} more.")
