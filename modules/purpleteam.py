"""Combined offensive/defensive lab exercises."""

from core.audit import log_tool_use
from core.loader import load_plugins

SCENARIOS = {
    "1": {
        "title": "Recon vs Detection",
        "description": "Scan a lab host, then review listeners and connections.",
        "steps": [
            ("red", "tool_1", "Port scan the authorized lab target"),
            ("red", "tool_8", "Grab banners from discovered services"),
            ("blue", "tool_3", "Audit listening ports on this host"),
            ("blue", "tool_9", "Diff current connections against a snapshot"),
        ],
    },
    "2": {
        "title": "Integrity Attack and Defense",
        "description": "Baseline files, change something, then detect it.",
        "steps": [
            ("blue", "tool_2", "Create a File Integrity Monitor baseline"),
            ("blue", "tool_35", "Watch a directory while you edit a file"),
            ("blue", "tool_2", "Re-check integrity and confirm the change"),
        ],
    },
    "3": {
        "title": "Credential Noise vs Blue Detection",
        "description": "Review auth failures and sudo activity after lab login tests.",
        "steps": [
            ("blue", "tool_1", "Analyze failed login patterns"),
            ("blue", "tool_8", "Review sudo command usage"),
            ("blue", "tool_34", "Look for repeated authentication anomalies"),
            ("blue", "tool_48", "Collect volatile evidence"),
        ],
    },
    "4": {
        "title": "Honeypot Engagement",
        "description": "Stand up a listener, generate traffic, review the log.",
        "steps": [
            ("blue", "tool_41", "Start the low-interaction honeypot"),
            ("red", "tool_8", "Banner-grab the honeypot from another terminal"),
            ("blue", "tool_49", "Open the honeypot log in Report Viewer"),
        ],
    },
}


def run(username: str, role: str) -> None:
    if role not in {"admin", "instructor"}:
        print("[!] Purple Team exercises are limited to instructors and admins.")
        return

    red = load_plugins("red")
    blue = load_plugins("blue")

    print("\n=== Purple Team Exercises ===")
    print("These are guided attack/defense labs. Use authorized targets only.\n")

    for key, scenario in SCENARIOS.items():
        print(f"  {key}. {scenario['title']}")
        print(f"     {scenario['description']}")
    print("  0. Back")

    choice = input("\nSelect exercise: ").strip()
    if choice not in SCENARIOS:
        return

    scenario = SCENARIOS[choice]
    print(f"\n*** {scenario['title']} ***")
    print(scenario["description"])

    for step_num, (team, tool_key, purpose) in enumerate(scenario["steps"], 1):
        catalog = red if team == "red" else blue
        plugin = catalog.get(tool_key)

        print(f"\n--- Step {step_num}/{len(scenario['steps'])} [{team.upper()}] ---")
        print(f"Purpose: {purpose}")

        if not plugin:
            print(f"[!] Missing plugin {tool_key}. Skipping.")
            continue

        print(f"Tool: {plugin['name']}")
        action = input("Enter to run, or type skip/quit: ").strip().lower()

        if action == "quit":
            print("[*] Exercise stopped.")
            return
        if action == "skip":
            continue

        status = "ok"
        try:
            plugin["run"](username, role)
        except Exception as exc:
            status = "error"
            print(f"[!] Step failed: {exc}")

        log_tool_use(username, role, f"purple/{team}", plugin["name"], status)

    print(f"\n[+] Purple Team exercise complete: {scenario['title']}")
    print("[*] Review reports in tools/red/reports and tools/blue/reports.")
