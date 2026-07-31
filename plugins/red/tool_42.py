from core.tool_runner import run_tool

NAME = "SMB/RPC Enumeration"
DESCRIPTION = "Full SMB user/share/policy enumeration (enum4linux-ng)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    target = input("Target IP: ").strip()
    if not target:
        return

    print("Options: (1) basic  (2) full (-A)")
    choice = input("Select [1]: ").strip() or "1"
    args = [target] if choice == "1" else ["-A", target]

    run_tool("enum4linux-ng", args, package="enum4linux-ng")
