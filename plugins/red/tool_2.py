from core.tool_runner import run_tool

NAME = "Service Detection"
DESCRIPTION = "Detect service versions on open ports (nmap -sV)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    target = input("Target IP/host (lab only): ").strip()
    if not target:
        return
    run_tool("nmap", ["-sV", target])
