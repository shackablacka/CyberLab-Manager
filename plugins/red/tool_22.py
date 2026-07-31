from pathlib import Path
from core.tool_runner import run_tool

NAME = "John the Ripper"
DESCRIPTION = "Crack hashes from a file using a wordlist."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    hash_file = input("Path to hash file: ").strip()
    if not Path(hash_file).is_file():
        print("[!] File not found.")
        return

    wordlist = input("Wordlist (blank = john default): ").strip()
    args = [hash_file]
    if wordlist:
        if not Path(wordlist).is_file():
            print("[!] Wordlist not found.")
            return
        args = [f"--wordlist={wordlist}", hash_file]

    run_tool("john", args, package="john")
    print("\n[*] Show cracked results with: john --show", hash_file)
