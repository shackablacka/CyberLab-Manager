from core.tool_runner import run_tool

NAME = "Whois Lookup"
DESCRIPTION = "Query domain registration records (whois)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    domain = input("Domain to look up: ").strip()
    if not domain:
        return
    run_tool("whois", [domain], package="whois")
