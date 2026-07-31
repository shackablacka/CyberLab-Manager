from core.loader import load_plugins

NAME = "Incident Response Launcher"
DESCRIPTION = "Guided IR workflow: gather evidence, analyze, report."
ALLOWED_ROLES = ["admin", "instructor"]

STEPS = [
    ("tool_1",  "failed_login_analyzer"),
    ("tool_4",  "process_auditor"),
    ("tool_9",  "connection_diff_monitor"),
    ("tool_7",  "user_account_auditor"),
    ("tool_2",  "file_integrity_monitor"),
]


def run(username, role):
    plugins = load_plugins("blue")

    print("\n=== Incident Response Workflow ===")
    print("This guided sequence gathers evidence in a logical order.")
    print("You'll be asked to run each step and confirm.\n")

    for step_num, (tool_key, _) in enumerate(STEPS, 1):
        plugin = plugins.get(tool_key)
        if not plugin:
            continue
        print(f"\n--- Step {step_num}/{len(STEPS)}: {plugin['name']} ---")
        input("Press Enter to run this step...")
        try:
            plugin["run"](username, role)
        except Exception as e:
            print(f"[!] Step failed: {e}")

        more = input("\nContinue with next step? (Y/n): ").strip().lower()
        if more == "n":
            print("[*] Workflow paused.")
            return

    print("\n[+] Incident Response workflow complete.")
    print("[*] Summarize findings in a report and preserve evidence logs.")
