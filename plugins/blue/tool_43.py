from pathlib import Path
from core.tool_runner import run_tool

NAME = "Lynis Security Audit"
DESCRIPTION = "Run a comprehensive system hardening audit (lynis)."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/blue/reports")


def run(username, role):
    print("[*] Lynis performs a thorough system security audit.")
    print("[*] This may take several minutes.\n")

    print("1. Full audit (recommended)")
    print("2. Quick scan")
    choice = input("Select [1]: ").strip() or "1"

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if choice == "1":
        run_tool(
            "lynis",
            ["audit", "system", "--no-colors", "--quick"],
            package="lynis",
        )
    else:
        run_tool(
            "lynis",
            ["audit", "system", "--no-colors", "--quick", "--tests-from-group",
             "authentication,networking,storage,firewalls"],
            package="lynis",
        )

    log_path = Path("/var/log/lynis.log")
    report_path = Path("/var/log/lynis-report.dat")

    if log_path.exists():
        print(f"\n[+] Full log: {log_path}")
    if report_path.exists():
        print(f"[+] Report data: {report_path}")
        # Extract hardening index
        for line in report_path.read_text(errors="ignore").splitlines():
            if "hardening_index" in line:
                print(f"[*] {line.strip()}")
