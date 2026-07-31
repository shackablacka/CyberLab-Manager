from core.tool_runner import run_tool

NAME = "Chkrootkit Scanner"
DESCRIPTION = "Run chkrootkit to check for common rootkit indicators."
ALLOWED_ROLES = ["admin", "instructor"]

def run(username, role):
    print("[*] This is a read-only rootkit scan.")
    run_tool("chkrootkit", [], package="chkrootkit")
