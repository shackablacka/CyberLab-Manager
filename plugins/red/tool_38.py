from pathlib import Path
from core.tool_runner import run_tool

NAME = "Gobuster"
DESCRIPTION = "Fast directory/DNS brute-forcing (gobuster)."
ALLOWED_ROLES = ["admin", "instructor"]

DEFAULT_WORDLIST = "/usr/share/wordlists/dirb/common.txt"


def run(username, role):
    print("[!] LAB USE ONLY — authorized targets only.")
    url = input("Target URL: ").strip()
    if not url:
        return
    if not url.startswith("http"):
        url = "http://" + url

    wordlist = input(f"Wordlist (default {DEFAULT_WORDLIST}): ").strip()
    wordlist = wordlist or DEFAULT_WORDLIST
    if not Path(wordlist).is_file():
        print(f"[!] Wordlist not found: {wordlist}")
        print("[*] Install with: apt install wordlists")
        return

    run_tool("gobuster", ["dir", "-u", url, "-w", wordlist],
             package="gobuster")
