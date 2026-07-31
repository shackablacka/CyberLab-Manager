from core.tool_runner import run_tool

NAME = "Exploit Search"
DESCRIPTION = "Search Exploit-DB for known vulnerabilities (searchsploit)."
ALLOWED_ROLES = ["admin", "instructor", "student"]


def run(username, role):
    query = input("Search term (e.g. 'apache 2.4.49'): ").strip()
    if not query:
        return
    run_tool("searchsploit", query.split(), package="exploitdb")
