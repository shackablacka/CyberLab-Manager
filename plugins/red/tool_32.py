from pathlib import Path
from core.tool_runner import run_tool

NAME = "Nmap Vuln Scripts"
DESCRIPTION = "Run nmap NSE vuln scripts against a lab host."
ALLOWED_ROLES = ["admin", "instructor"]

REPORT_DIR = Path("tools/red/reports")


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    target = input("Target IP/host: ").strip()
    if not target:
        return

    safe = "".join(c for c in target if c.isalnum() or c in ".-")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"nse_vuln_{safe}.txt"

    print(f"[*] Results will be saved to {out}")
    run_tool(
        "nmap",
        ["--script", "vuln", "-oN", str(out), target],
        package="nmap",
    )
