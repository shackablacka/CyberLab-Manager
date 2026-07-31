from core.loader import load_plugins

NAME = "Blue Team Exercise Launcher"
DESCRIPTION = "Guided defensive scenario: detect, analyze, respond."
ALLOWED_ROLES = ["admin", "instructor"]

SCENARIOS = {
    "1": {
        "title": "Brute-Force Detection and Response",
        "description": "Identify brute-force attempts, trace the source, "
                       "review fail2ban, and collect evidence.",
        "steps": [
            ("tool_1",  "Analyze failed logins"),
            ("tool_34", "Detect log anomalies"),
            ("tool_14", "Check fail2ban status"),
            ("tool_9",  "Snapshot active connections"),
            ("tool_48", "Collect volatile evidence"),
        ],
    },
    "2": {
        "title": "Suspicious Process Investigation",
        "description": "Find unauthorized processes, check integrity, "
                       "review privileged execution.",
        "steps": [
            ("tool_4",  "Audit running processes"),
            ("tool_39", "Review privileged processes"),
            ("tool_29", "Watch for new processes"),
            ("tool_2",  "Check file integrity"),
            ("tool_37", "Audit kernel modules"),
        ],
    },
    "3": {
        "title": "Full Security Posture Review",
        "description": "Comprehensive hardening check: firewall, SSH, "
                       "permissions, services, and scoring.",
        "steps": [
            ("tool_47", "Run hardening scorecard"),
            ("tool_13", "Audit SSH configuration"),
            ("tool_27", "Find weak file permissions"),
            ("tool_36", "Audit sudoers"),
            ("tool_26", "Review boot services"),
            ("tool_40", "Compare security baseline"),
        ],
    },
}


def run(username, role):
    plugins = load_plugins("blue")

    print("\n=== Blue Team Guided Exercises ===\n")
    for key, scenario in SCENARIOS.items():
        print(f"  {key}. {scenario['title']}")
        print(f"     {scenario['description']}\n")
    print("  0. Cancel")

    choice = input("Select exercise: ").strip()
    if choice not in SCENARIOS:
        return

    scenario = SCENARIOS[choice]
    steps = scenario["steps"]

    print(f"\n{'=' * 50}")
    print(f"  {scenario['title']}")
    print(f"  {scenario['description']}")
    print(f"  {len(steps)} step(s)")
    print(f"{'=' * 50}")

    for step_num, (tool_key, description) in enumerate(steps, 1):
        plugin = plugins.get(tool_key)
        if not plugin:
            print(f"\n[!] Step {step_num}: plugin {tool_key} not found — skipping.")
            continue

        print(f"\n--- Step {step_num}/{len(steps)}: {plugin['name']} ---")
        print(f"    Purpose: {description}")
        proceed = input("    Press Enter to run (or 'skip' / 'quit'): ").strip().lower()

        if proceed == "quit":
            print("[*] Exercise ended early.")
            return
        if proceed == "skip":
            print("    (skipped)")
            continue

        try:
            plugin["run"](username, role)
        except Exception as e:
            print(f"[!] Step failed: {e}")

    print(f"\n{'=' * 50}")
    print(f"[+] Exercise '{scenario['title']}' complete!")
    print("[*] Review collected reports with: Blue Team Report Viewer")
    print(f"{'=' * 50}")
