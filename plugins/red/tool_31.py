from core.tool_runner import run_tool

NAME = "Nikto Web Scanner"
DESCRIPTION = "Full web server vulnerability scan (nikto)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    target = input("Target host or URL: ").strip()
    if not target:
        return
    run_tool("nikto", ["-h", target], package="nikto")
