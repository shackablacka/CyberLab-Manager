from pathlib import Path
from core.tool_runner import run_tool

NAME = "SQLMap"
DESCRIPTION = "Automated SQL injection testing (sqlmap)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("[!] LAB USE ONLY — sqlmap sends aggressive payloads.")
    confirm = input("Type 'LAB' to confirm authorized target: ").strip()
    if confirm != "LAB":
        print("[!] Aborted.")
        return

    url = input("Target URL with parameter (e.g. http://lab/item.php?id=1): ").strip()
    if not url or "=" not in url:
        print("[!] URL must contain a query parameter.")
        return

    level = input("Level 1-5 (default 1): ").strip() or "1"
    run_tool(
        "sqlmap",
        ["-u", url, "--batch", f"--level={level}", "--risk=1"],
        package="sqlmap",
    )
