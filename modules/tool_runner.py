"""Shared tool execution engine for red and blue team modules."""

import shlex
import shutil
import sqlite3
import subprocess
import logging
from datetime import datetime

from core.auth import DATABASE

log = logging.getLogger("cyberlab.tools")

FORBIDDEN_CHARS = set(";|&$`\\\"'{}()<>!\n\r")


def sanitize(text: str) -> str | None:
    if any(c in FORBIDDEN_CHARS for c in text):
        return None
    return text.strip()


def get_user_id(username: str) -> int | None:
    conn = sqlite3.connect(DATABASE)
    row = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row[0] if row else None


def check_tool(binary: str) -> bool:
    return shutil.which(binary) is not None


def run_command(cmd: list[str], timeout: int = 300) -> tuple[str, int]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = r.stdout
        if r.stderr:
            output += "\n[STDERR]\n" + r.stderr
        return output, r.returncode
    except subprocess.TimeoutExpired:
        return f"[!] Command timed out after {timeout}s.", -1
    except FileNotFoundError:
        return "[!] Binary not found.", -1
    except Exception as e:
        return f"[!] Error: {e}", -1


def save_scan(user_id: int, tool: str, target: str, args: str,
              output: str, status: str, team: str) -> int:
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO scan_results(user_id, tool, target, arguments, output, status, finished_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, tool, target, args, output[:50000], status, datetime.now().isoformat()),
    )
    cur.execute(
        "INSERT INTO tool_audit(user_id, team, tool_name, target) VALUES (?, ?, ?, ?)",
        (user_id, team, tool, target),
    )
    scan_id = cur.lastrowid
    conn.commit()
    conn.close()
    return scan_id


def save_event(event_type: str, severity: str, source: str,
               description: str, raw_data: str = ""):
    conn = sqlite3.connect(DATABASE)
    conn.execute(
        """INSERT INTO security_events(event_type, severity, source, description, raw_data)
           VALUES (?, ?, ?, ?, ?)""",
        (event_type, severity, source, description, raw_data[:50000]),
    )
    conn.commit()
    conn.close()


def execute_tool(username: str, tool_def: dict, team: str) -> None:
    binary = tool_def["binary"]
    name = tool_def.get("name", binary)
    default_flags = tool_def.get("flags", [])
    needs_target = tool_def.get("target", True)
    timeout = tool_def.get("timeout", 300)
    target_label = tool_def.get("target_label", "Target")
    custom_handler = tool_def.get("handler")

    if not check_tool(binary):
        print(f"[!] '{binary}' is not installed. Try: apt install {binary}")
        return

    if custom_handler:
        custom_handler(username, tool_def, team)
        return

    target = ""
    if needs_target:
        raw = input(f"{target_label}: ").strip()
        target = sanitize(raw)
        if not target:
            print("[!] Invalid target.")
            return

    flag_input = input(f"Extra flags (default: {' '.join(default_flags)}): ").strip()
    if flag_input:
        try:
            flags = shlex.split(sanitize(flag_input) or "")
        except ValueError:
            print("[!] Invalid flags.")
            return
    else:
        flags = list(default_flags)

    cmd = [binary] + flags
    if needs_target:
        cmd.append(target)

    print(f"\n[*] Running: {' '.join(cmd)}")
    print(f"[*] Timeout: {timeout}s\n")

    user_id = get_user_id(username)
    output, rc = run_command(cmd, timeout)
    status = "completed" if rc == 0 else "failed"

    save_scan(user_id, name, target, " ".join(flags), output, status, team)

    display = output[:3000]
    print(display)
    if len(output) > 3000:
        print(f"\n... [truncated - full output saved, {len(output)} chars total]")
    print(f"\n[+] {name} {status}.")
