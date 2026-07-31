"""Shared helpers for checking and optionally installing system tools."""

import logging
import shutil
import subprocess
from typing import Sequence

log = logging.getLogger("cyberlab.tool_runner")


def is_installed(binary: str) -> bool:
    return shutil.which(binary) is not None


def install_tool(package: str) -> bool:
    """Install one apt package after explicit user confirmation."""
    if shutil.which("apt-get") is None:
        print("[!] apt-get is not available on this system.")
        return False

    confirm = input(
        f"[?] '{package}' is missing. Install it with apt? (y/N): "
    ).strip().lower()

    if confirm != "y":
        print("[!] Installation skipped.")
        return False

    command = ["sudo", "apt-get", "install", "-y", package]

    try:
        result = subprocess.run(command, check=False)
    except KeyboardInterrupt:
        print("\n[!] Installation interrupted.")
        return False
    except OSError as exc:
        print(f"[!] Could not start installer: {exc}")
        return False

    if result.returncode != 0:
        print(f"[!] Installation failed with exit code {result.returncode}.")
        return False

    if not is_installed(package):
        print(f"[!] Package installed, but '{package}' was not found in PATH.")
        return False

    print(f"[+] {package} installed successfully.")
    return True


def run_tool(
    binary: str,
    args: Sequence[str] = (),
    package: str | None = None,
) -> int | None:
    """Run a tool, offering to install it when missing."""
    package = package or binary

    if not is_installed(binary):
        print(f"[!] '{binary}' is not installed.")

        if not install_tool(package):
            return None

        if not is_installed(binary):
            print(f"[!] '{binary}' is still unavailable.")
            return None

    command = [binary, *args]
    print(f"[*] Running: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n[!] Tool interrupted.")
        return 130
    except OSError as exc:
        print(f"[!] Tool execution failed: {exc}")
        log.exception("Tool execution failed: %s", binary)
        return None
