from core.loader import load_plugins

NAME = "Lab Exercise Launcher"
DESCRIPTION = "Guided scenario: chains recon -> scan -> audit tools."
ALLOWED_ROLES = ["admin", "instructor"]

SCENARIOS = {
    "1": {
        "title": "Basic Host Assessment",
        "description": "Discover a host, scan it, and inspect its web surface.",
        "steps": ["tool_3", "tool_1", "tool_8", "tool_5"],
    },
    "2": {
        "title": "Web App Audit",
        "description": "Headers, robots.txt, methods, then vuln probes.",
        "steps": ["tool_5", "tool_15", "tool_14", "tool_26", "tool_24"],
    },
    "3": {
        "title": "Credential Hygiene",
        "description": "Hash ID, strength audit, and basic-auth testing.",
        "steps": ["tool_21", "tool_29", "tool_28"],
    },
}


def run(username, role):
    plugins = load_plugins("red")

    print("\n=== Guided Lab Exercises ===")
    for key, sc in SCENARIOS.items():
        print(f"  {key}. {sc['title']} — {sc['description']}")
    print("  0. Cancel")

    choice = input("\nSelect exercise: ").strip()
    if choice not in SCENARIOS:
        return

    scenario = SCENARIOS[choice]
    print(f"\n*** {scenario['title']} ***")
    print(f"{scenario['description']}\n")

    for step_num, tool_key in enumerate(scenario["steps"], 1):
        plugin = plugins.get(tool_key)
        if not plugin:
            continue
        print(f"\n--- Step {step_num}/{len(scenario['steps'])}: {plugin['name']} ---")
        input("Press Enter to run this step...")
        try:
            plugin["run"](username, role)
        except Exception as e:
            print(f"[!] Step failed: {e}")

        more = input("\nContinue to next step? (Y/n): ").strip().lower()
        if more == "n":
            print("[*] Exercise paused.")
            return

    print(f"\n[+] Exercise '{scenario['title']}' complete!")
    print("[*] Review findings in Report Viewer (tool 37).")
