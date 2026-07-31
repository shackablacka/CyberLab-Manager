from core.tool_runner import run_tool

NAME = "SMB Share Enumerator"
DESCRIPTION = "List shares on a lab Windows/Samba host (smbclient)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    target = input("Target IP (lab only): ").strip()
    if not target:
        return
    run_tool("smbclient", ["-L", f"//{target}", "-N"], package="smbclient")
