import subprocess
from pathlib import Path
from core.tool_runner import run_tool

NAME = "PrivEsc Helper (LinPEAS)"
DESCRIPTION = "Run LinPEAS or a native quick privesc checklist."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/red/reports")


def run(username, role):
    print("1. Run LinPEAS (if present)")
    print("2. Native quick privesc checklist")
    choice = input("Select: ").strip()

    if choice == "1":
        candidates = [Path("/usr/share/peass/linpeas/linpeas.sh"),
                      Path("/opt/linpeas/linpeas.sh"),
                      Path("./linpeas.sh")]
        script = next((p for p in candidates if p.is_file()), None)
        if script:
            run_tool("bash", [str(script)], package="peass-ng")
        else:
            print("[!] linpeas.sh not found locally.")
            print("[*] Download it to a lab VM, then run option 1 again.")
    elif choice == "2":
        native_checklist()
    else:
        print("[!] Invalid choice.")


def native_checklist():
    checks = [
        ("Kernel / OS", ["uname", "-a"]),
        ("Current user", ["id"]),
        ("Sudo rights", ["sudo", "-ln"]),
        ("SUID binaries (top 20)",
         ["bash", "-c", "find / -perm -4000 -type f 2>/dev/null | head -20"]),
        ("Writable /etc/passwd?", ["bash", "-c", "ls -l /etc/passwd /etc/shadow"]),
        ("Cron jobs", ["bash", "-c", "cat /etc/crontab; ls /etc/cron* 2>/dev/null"]),
    ]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / "privesc_checklist.txt"

    lines = []
    for title, cmd in checks:
        print(f"\n=== {title} ===")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        text = result.stdout.strip() or "(no output)"
        print(text[:600])
        lines.append(f"=== {title} ===\n{text}\n")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[+] Checklist saved to {out}")
