from core.tool_runner import run_tool

NAME = "Package Integrity (debsums)"
DESCRIPTION = "Verify installed package file checksums (debsums)."
ALLOWED_ROLES = ["admin", "instructor"]


def run(username, role):
    print("[*] Verifying package file integrity with debsums...")
    print("[*] This may take several minutes on a full system.\n")
    run_tool("debsums", ["-a"], package="debsums")
    print("\n[*] Tip: 'debsums -c' only reports changed files.")
