from core.tool_runner import run_tool

NAME = "Hydra Login Brute-Forcer"
DESCRIPTION = "Online password attack against lab services (hydra)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("[!] LAB USE ONLY — only against systems you own or have")
    print("    explicit written permission to test.")
    confirm = input("Type 'LAB' to confirm authorized target: ").strip()
    if confirm != "LAB":
        print("[!] Aborted.")
        return

    target = input("Target IP: ").strip()
    service = input("Service (ssh/ftp/http-get/smb/rdp): ").strip().lower()
    user = input("Username (or path to user list): ").strip()
    wordlist = input("Password wordlist: ").strip()

    if not all([target, service, user, wordlist]):
        print("[!] All fields required.")
        return

    user_arg = ["-L", user] if "/" in user else ["-l", user]
    args = user_arg + ["-P", wordlist, "-t", "4", target, service]
    run_tool("hydra", args, package="hydra")
