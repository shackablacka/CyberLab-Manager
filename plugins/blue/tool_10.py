from pathlib import Path
from core.tool_runner import run_tool

NAME = "Malware Scanner (ClamAV)"
DESCRIPTION = "Scan files/directories for malware (clamscan)."
ALLOWED_ROLES = ["admin", "instructor", "student"]

REPORT_DIR = Path("tools/blue/reports")


def run(username, role):
    target = input("File or directory to scan: ").strip()
    if not target or not Path(target).exists():
        print("[!] Valid path required.")
        return

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / "clamav_scan.log"

    args = ["-r", "--log", str(out), target]
    print(f"[*] Scanning {target} (report: {out})...")
    run_tool("clamscan", args, package="clamav")

    print("\n[*] Tip: update signatures with 'freshclam' before scanning.")
