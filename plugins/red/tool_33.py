from core.tool_runner import run_tool

NAME = "WPScan"
DESCRIPTION = "WordPress vulnerability scanner (wpscan)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    url = input("WordPress site URL: ").strip()
    if not url:
        return
    if not url.startswith("http"):
        url = "http://" + url

    print("Enumerate: (1) plugins  (2) users  (3) themes  (4) all")
    choice = input("Select [4]: ").strip() or "4"
    enum = {"1": "p", "2": "u", "3": "t", "4": "u,p,t"}.get(choice, "u,p,t")

    run_tool("wpscan", ["--url", url, "--enumerate", enum], package="wpscan")
