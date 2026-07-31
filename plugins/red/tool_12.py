from core.tool_runner import run_tool

NAME = "SNMP Walker"
DESCRIPTION = "Query SNMP info from a lab device (snmpwalk)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    target = input("Target IP (lab only): ").strip()
    if not target:
        return
    community = input("Community string (default public): ").strip() or "public"
    run_tool("snmpwalk", ["-v2c", "-c", community, target], package="snmp")
