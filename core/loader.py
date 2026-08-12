"""Dynamic plugin loader for CyberLab-Manager."""

import importlib
import logging
import pkgutil
import sys
from pathlib import Path
from typing import Any

from core.audit import log_tool_use

log = logging.getLogger("cyberlab.loader")


def load_plugins(category: str) -> dict[str, dict[str, Any]]:
    plugins: dict[str, dict[str, Any]] = {}
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
                run_func = getattr(module, "run", None)

                if not callable(run_func):
                    log.warning("Skipping %s: missing run()", module_name)
                    continue

                plugins[module_name] = {
                    "name": getattr(
                        module,
                        "NAME",
                        module_name.replace("_", " ").title(),
                    ),
                    "description": getattr(
                        module,
                        "DESCRIPTION",
                        "No description provided.",
                    ),
                    "allowed_roles": getattr(
                        module,
                        "ALLOWED_ROLES",
                        ["admin", "instructor"],
                    ),
                    "run": run_func,
                }
            except Exception as exc:
                log.error("Failed to load %s: %s", module_name, exc, exc_info=True)
    finally:
        if sys_path_added:
            sys.path.remove(package_dir)

    return plugins


def run_plugin_menu(category: str, username: str, role: str) -> None:
    while True:
        plugins = load_plugins(category)
        authorized = {
            key: plugin
            for key, plugin in plugins.items()
            if role in plugin["allowed_roles"]
        }

        print(f"\n=== {category.upper()} TEAM PLUGINS ===")
        print(f"Available: {len(authorized)}")

        if not authorized:
            print("No authorized plugins available for your role.")
            input("\nPress Enter to return...")
            return

        sorted_keys = sorted(
            authorized.keys(),
            key=lambda key: authorized[key]["name"].lower(),
        )

        for index, key in enumerate(sorted_keys, 1):
            plugin = authorized[key]
            print(f"{index:2d}. {plugin['name']:<32} {plugin['description']}")
        print(" 0. Back to Main Menu")

        choice = input("\nSelect plugin to execute: ").strip()
        if choice == "0":
            return

        if not choice.isdigit():
            print("[!] Please enter a number.")
            continue

        index = int(choice) - 1
        if not 0 <= index < len(sorted_keys):
            print("[!] Invalid option.")
            continue

        key = sorted_keys[index]
        plugin = authorized[key]
        print(f"\n--- Running: {plugin['name']} ---")
        status = "ok"

        try:
            plugin["run"](username, role)
        except Exception as exc:
            status = "error"
            print(f"[!] Plugin error: {exc}")
            log.error("Plugin %s failed", key, exc_info=True)

        log_tool_use(username, role, category, plugin["name"], status)
        input("\nPress Enter to continue...")
