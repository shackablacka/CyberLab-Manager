from core.tool_runner import run_tool

NAME = "Rootkit Scanner"
DESCRIPTION = "Scan for rootkits (rkhunter / chkrootkit)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("1. rkhunter (thorough, interactive)")
    print("2. chkrootkit (quick)")
    choice = input("Select: ").strip()

    if choice == "1":
        run_tool("rkhunter", ["--check", "--sk"], package="rkhunter")
        print("\n[*] Full log: /var/log/rkhunter.log")
    elif choice == "2":
        run_tool("chkrootkit", [], package="chkrootkit")
    else:
        print("[!] Invalid choice.")
