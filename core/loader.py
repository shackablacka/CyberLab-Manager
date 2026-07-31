"""Dynamic plugin loader for CyberLab-Manager."""

import importlib
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Dict, Any

log = logging.getLogger("cyberlab.loader")


def load_plugins(category: str) -> Dict[str, Dict[str, Any]]:
    """Discover and load plugins from plugins/<category>/."""
    plugins = {}
    package_path = Path("plugins") / category

    if not package_path.exists():
        log.warning("Plugin path %s does not exist.", package_path)
        return plugins

    sys_path_added = False
    package_dir = str(package_path.resolve())
    if package_dir not in sys.path:
        sys.path.insert(0, package_dir)
        sys_path_added = True

    try:
        for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
            full_module_name = f"plugins.{category}.{module_name}"

            if full_module_name in sys.modules:
                del sys.modules[full_module_name]

            try:
                module = importlib.import_module(full_module_name)

                name = getattr(module, "NAME", module_name.replace("_", " ").title())
                description = getattr(module, "DESCRIPTION", "No description provided.")
                allowed_roles = getattr(module, "ALLOWED_ROLES", ["admin", "instructor"])
                run_func = getattr(module, "run", None)

                if not callable(run_func):
                    log.warning("Skipping %s: missing run()", module_name)
                    continue

                plugins[module_name] = {
                    "name": name,
                    "description": description,
                    "allowed_roles": allowed_roles,
                    "run": run_func,
                }
            except Exception as e:
                log.error("Failed to load %s: %s", module_name, e, exc_info=True)
    finally:
        if sys_path_added:
            sys.path.remove(package_dir)

    return plugins


def run_plugin_menu(category: str, username: str, role: str) -> None:
    """Display the menu and dispatch user choices."""
    while True:
        plugins = load_plugins(category)
        authorized = {k: v for k, v in plugins.items() if role in v["allowed_roles"]}

        print(f"\n=== {category.upper()} TEAM PLUGINS ===")
        if not authorized:
            print("No authorized plugins available for your role.")
            print("0. Back")
            input("\nPress Enter to return...")
            return

        sorted_keys = sorted(authorized.keys(), key=lambda x: authorized[x]["name"])

        for i, key in enumerate(sorted_keys, 1):
            plugin = authorized[key]
            print(f"{i:2d}. {plugin['name']:<30} - {plugin['description']}")
        print(" 0. Back to Main Menu")

        choice = input("\nSelect plugin to execute: ").strip()

        if choice == "0":
            return

        try:
            index = int(choice) - 1
            if 0 <= index < len(sorted_keys):
                key = sorted_keys[index]
                plugin = authorized[key]
                log.info("User %s executing %s plugin: %s", username, category, plugin["name"])
                print(f"\n--- Running: {plugin['name']} ---")
                try:
                    plugin["run"](username, role)
                except Exception as e:
                    print(f"[!] Plugin error: {e}")
                    log.error("Plugin %s failed", key, exc_info=True)
                input("\nPress Enter to continue...")
            else:
                print("[!] Invalid option.")
        except ValueError:
            print("[!] Please enter a number.")
