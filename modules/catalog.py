"""Browse Red/Blue plugins and recent usage."""

from core.audit import recent_usage, usage_summary
from core.loader import load_plugins


def run(username: str, role: str) -> None:
    while True:
        print("\n=== Tool Catalog ===")
        print("1. Browse Red Team tools")
        print("2. Browse Blue Team tools")
        print("3. Search tools")
        print("4. Recent usage")
        print("5. Most-used tools")
        print("0. Back")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            return
        if choice == "1":
            show_catalog("red", role)
        elif choice == "2":
            show_catalog("blue", role)
        elif choice == "3":
            search_tools(role)
        elif choice == "4":
            show_recent()
        elif choice == "5":
            show_summary()
        else:
            print("[!] Invalid option.")


def show_catalog(team: str, role: str) -> None:
    plugins = load_plugins(team)
    print(f"\n=== {team.upper()} TEAM CATALOG ({len(plugins)}) ===")

    for index, key in enumerate(sorted(plugins, key=lambda k: plugins[k]["name"]), 1):
        plugin = plugins[key]
        allowed = "yes" if role in plugin["allowed_roles"] else "no"
        print(f"{index:2d}. {plugin['name']:<32} {plugin['description']}")
        print(f"    roles={','.join(plugin['allowed_roles'])}  access={allowed}")


def search_tools(role: str) -> None:
    query = input("Search term: ").strip().lower()
    if not query:
        return

    hits = []
    for team in ("red", "blue"):
        for plugin in load_plugins(team).values():
            haystack = f"{plugin['name']} {plugin['description']}".lower()
            if query in haystack:
                hits.append((team, plugin))

    print(f"\n[+] {len(hits)} match(es) for '{query}'")
    for team, plugin in hits:
        access = "yes" if role in plugin["allowed_roles"] else "no"
        print(f"  [{team}] {plugin['name']:<32} {plugin['description']}  access={access}")


def show_recent() -> None:
    rows = recent_usage(20)
    if not rows:
        print("\n[*] No tool usage recorded yet.")
        return

    print("\n=== Recent Tool Usage ===")
    print(f"{'When':<20} {'User':<12} {'Team':<6} {'Status':<7} Tool")
    print("-" * 78)
    for created_at, user, _role, team, tool_name, status in rows:
        print(f"{created_at:<20} {user:<12} {team:<6} {status:<7} {tool_name}")


def show_summary() -> None:
    rows = usage_summary()
    if not rows:
        print("\n[*] No usage summary yet.")
        return

    print("\n=== Most-Used Tools ===")
    for team, tool_name, uses in rows[:25]:
        print(f"  {uses:>4}  [{team}] {tool_name}")
