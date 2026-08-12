"""Shared Red/Blue Team tool execution engine with Shock HUD live runner.
Author: Sblacka
"""

import shlex
import shutil
import sqlite3
import subprocess
import logging
import time
import random
import select
from datetime import datetime
from pathlib import Path

from core.auth import DATABASE

log = logging.getLogger("cyberlab.tools")

# Do not use shell=True, but still reject obvious shell-control characters.
FORBIDDEN_CHARS = set(";|$`\\{}\n\r")

try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.live import Live
    from rich import box

    HAS_RICH = True
    console = Console()
except Exception:
    HAS_RICH = False
    console = None


CYAN = "#00e5ff"
GREEN = "#00ff41"
RED = "#ff0055"
AMBER = "#ffb000"
PURPLE = "#bd00ff"
BLUE = "#3388ff"
WHITE = "#e8ecf3"
DIM = "#667085"
BLACK = "#05070d"
PANEL_BG = "#0b0f19"


def sanitize(text: str) -> str | None:
    """Basic input sanitizer for targets/flags."""
    if text is None:
        return None

    if any(c in FORBIDDEN_CHARS for c in text):
        return None

    return text.strip()


def get_user_id(username: str) -> int | None:
    conn = sqlite3.connect(DATABASE)
    row = conn.execute(
        "SELECT id FROM users WHERE username=?",
        (username,),
    ).fetchone()
    conn.close()
    return row[0] if row else None


def check_tool(binary: str) -> bool:
    return shutil.which(binary) is not None


def _columns(conn, table: str) -> set[str]:
    try:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    except sqlite3.OperationalError:
        return set()


def _add_column(conn, table: str, column: str, definition: str):
    if column not in _columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def ensure_tool_tables():
    """Create or migrate Red/Blue tool tracking tables safely."""
    db = Path(str(DATABASE))
    db.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tool TEXT,
                target TEXT,
                arguments TEXT,
                output TEXT,
                status TEXT DEFAULT 'completed',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                severity TEXT DEFAULT 'info',
                source TEXT,
                description TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tool_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                team TEXT,
                tool_name TEXT,
                target TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Safe migrations for older database files.
        _add_column(conn, "scan_results", "user_id", "INTEGER")
        _add_column(conn, "scan_results", "tool", "TEXT")
        _add_column(conn, "scan_results", "target", "TEXT")
        _add_column(conn, "scan_results", "arguments", "TEXT")
        _add_column(conn, "scan_results", "output", "TEXT")
        _add_column(conn, "scan_results", "status", "TEXT")
        _add_column(conn, "scan_results", "started_at", "TEXT")
        _add_column(conn, "scan_results", "finished_at", "TEXT")

        _add_column(conn, "security_events", "event_type", "TEXT")
        _add_column(conn, "security_events", "severity", "TEXT")
        _add_column(conn, "security_events", "source", "TEXT")
        _add_column(conn, "security_events", "description", "TEXT")
        _add_column(conn, "security_events", "raw_data", "TEXT")
        _add_column(conn, "security_events", "created_at", "TEXT")

        _add_column(conn, "tool_audit", "user_id", "INTEGER")
        _add_column(conn, "tool_audit", "team", "TEXT")
        _add_column(conn, "tool_audit", "tool_name", "TEXT")
        _add_column(conn, "tool_audit", "target", "TEXT")
        _add_column(conn, "tool_audit", "started_at", "TEXT")

        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_scan_results_user_id
                ON scan_results(user_id);

            CREATE INDEX IF NOT EXISTS idx_scan_results_tool
                ON scan_results(tool);

            CREATE INDEX IF NOT EXISTS idx_scan_results_started_at
                ON scan_results(started_at);

            CREATE INDEX IF NOT EXISTS idx_security_events_severity
                ON security_events(severity);

            CREATE INDEX IF NOT EXISTS idx_security_events_created_at
                ON security_events(created_at);

            CREATE INDEX IF NOT EXISTS idx_tool_audit_user_id
                ON tool_audit(user_id);

            CREATE INDEX IF NOT EXISTS idx_tool_audit_team
                ON tool_audit(team);
            """
        )

        conn.commit()


def _matrix_line(width=48):
    chars = "01abcdefABCDEF░▒▓"
    return "".join(random.choice(chars) for _ in range(width))


def _moving_bar(elapsed: float, width=36):
    pos = int(elapsed * 8) % width
    chars = []

    for i in range(width):
        if i == pos:
            chars.append("█")
        elif abs(i - pos) == 1:
            chars.append("▓")
        elif abs(i - pos) == 2:
            chars.append("▒")
        else:
            chars.append("░")

    return "".join(chars)


def _style_output_line(line: str):
    text = Text()
    low = line.lower()

    if "[!]" in line or "error" in low or "failed" in low or "timeout" in low:
        text.append(line, style=f"bold {RED}")
    elif "[+]" in line or "open" in low or "completed" in low:
        text.append(line, style=f"bold {GREEN}")
    elif "[*]" in line or "starting" in low or "running" in low:
        text.append(line, style=f"bold {CYAN}")
    elif "warning" in low:
        text.append(line, style=f"bold {AMBER}")
    else:
        text.append(line, style=WHITE)

    return text


def _build_tool_hud(cmd, elapsed, timeout, output_lines, status="RUNNING", rc=None):
    command = shlex.join(cmd)
    timeout_text = f"{timeout}s" if timeout else "∞"

    header = Text()
    header.append("▣ ", style=f"bold {GREEN}")
    header.append("SHOCK HUD", style=f"bold {CYAN}")
    header.append("  //  ", style=DIM)
    header.append("TOOL EXECUTION MONITOR", style=f"bold {WHITE}")
    header.append("  //  ", style=DIM)

    if status == "RUNNING":
        header.append("ACTIVE", style=f"bold {GREEN}")
    elif status == "TIMEOUT":
        header.append("TIMEOUT", style=f"bold {AMBER}")
    elif rc == 0:
        header.append("COMPLETED", style=f"bold {GREEN}")
    else:
        header.append("FAILED", style=f"bold {RED}")

    meta = Table.grid(expand=True)
    meta.add_column(ratio=1)
    meta.add_column(ratio=1)
    meta.add_row(
        f"[bold {CYAN}]Command[/bold {CYAN}] [white]{command[:110]}[/white]",
        f"[bold {CYAN}]Elapsed[/bold {CYAN}] [white]{elapsed:0.1f}s[/white]   "
        f"[bold {CYAN}]Timeout[/bold {CYAN}] [white]{timeout_text}[/white]",
    )

    activity = Text()
    activity.append("\nSCAN BUS  ", style=DIM)
    activity.append(_moving_bar(elapsed), style=f"bold {GREEN}")
    activity.append("\n\nSIGNAL    ", style=DIM)
    activity.append(_matrix_line(60), style=f"bold {GREEN}")
    activity.append("\nAUTHOR    ", style=DIM)
    activity.append("SBLACKA", style=f"bold {PURPLE}")

    tail = Text()
    tail.append("LIVE OUTPUT TAIL\n", style=f"bold {CYAN}")

    recent = output_lines[-14:] if output_lines else ["waiting for output..."]
    for line in recent:
        tail.append_text(_style_output_line(line[:150]))
        tail.append("\n")

    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=2)
    grid.add_row(
        Panel(activity, border_style=GREEN, box=box.SQUARE, style=f"on {PANEL_BG}"),
        Panel(tail, border_style=CYAN, box=box.SQUARE, style=f"on {PANEL_BG}"),
    )

    return Panel(
        Group(header, meta, grid),
        title=f"[bold {GREEN}]SBLACKA // CYBERLAB-MANAGER[/bold {GREEN}]",
        border_style=GREEN if status == "RUNNING" else AMBER if status == "TIMEOUT" else CYAN,
        box=box.DOUBLE,
        style=f"on {BLACK}",
    )


def _run_command_plain(cmd: list[str], timeout: int = 300) -> tuple[str, int]:
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
    except KeyboardInterrupt:
        return "[!] Interrupted by user.", 130
    except Exception as e:
        return f"[!] Error: {e}", -1


def run_command(cmd: list[str], timeout: int = 300) -> tuple[str, int]:
    """Run command with Shock HUD live terminal interface."""
    if not HAS_RICH:
        return _run_command_plain(cmd, timeout)

    output_lines = []
    start = time.time()
    rc = None
    status = "RUNNING"

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            errors="replace",
        )
    except FileNotFoundError:
        return "[!] Binary not found.", -1
    except Exception as e:
        return f"[!] Error: {e}", -1

    try:
        with Live(
            _build_tool_hud(cmd, 0, timeout, output_lines),
            console=console,
            refresh_per_second=10,
            screen=False,
        ) as live:
            while True:
                elapsed = time.time() - start

                if timeout and elapsed > timeout and proc.poll() is None:
                    status = "TIMEOUT"
                    proc.terminate()
                    time.sleep(0.5)
                    if proc.poll() is None:
                        proc.kill()
                    rc = -1
                    output_lines.append(f"[!] Command timed out after {timeout}s.")
                    break

                if proc.stdout:
                    ready, _, _ = select.select([proc.stdout], [], [], 0.05)
                    if ready:
                        line = proc.stdout.readline()
                        if line:
                            output_lines.append(line.rstrip("\n"))

                rc = proc.poll()
                live.update(_build_tool_hud(cmd, elapsed, timeout, output_lines, status, rc))

                if rc is not None:
                    if proc.stdout:
                        for line in proc.stdout.readlines():
                            if line:
                                output_lines.append(line.rstrip("\n"))
                    break

                time.sleep(0.05)

            elapsed = time.time() - start
            final_status = "TIMEOUT" if status == "TIMEOUT" else "DONE"
            live.update(_build_tool_hud(cmd, elapsed, timeout, output_lines, final_status, rc))
            time.sleep(0.4)

    except KeyboardInterrupt:
        proc.terminate()
        output_lines.append("[!] Interrupted by user.")
        rc = 130
    except Exception as e:
        proc.terminate()
        output_lines.append(f"[!] Runner error: {e}")
        rc = -1

    return "\n".join(output_lines), rc if rc is not None else -1


def save_scan(
    user_id: int | None,
    tool: str,
    target: str,
    args: str,
    output: str,
    status: str,
    team: str,
) -> int:
    ensure_tool_tables()

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO scan_results(user_id, tool, target, arguments, output, status, finished_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            tool,
            target,
            args,
            output[:50000],
            status,
            datetime.now().isoformat(),
        ),
    )

    scan_id = cur.lastrowid

    cur.execute(
        """
        INSERT INTO tool_audit(user_id, team, tool_name, target, started_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            team,
            tool,
            target,
            datetime.now().isoformat(),
        ),
    )

    conn.commit()
    conn.close()
    return scan_id


def save_event(
    event_type: str,
    severity: str,
    source: str,
    description: str,
    raw_data: str = "",
):
    ensure_tool_tables()

    conn = sqlite3.connect(DATABASE)
    conn.execute(
        """
        INSERT INTO security_events(event_type, severity, source, description, raw_data, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            event_type,
            severity,
            source,
            description,
            raw_data[:50000],
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def execute_tool(username: str, tool_def: dict, team: str) -> None:
    """Generic tool executor driven by a registry definition."""
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
        safe_flags = sanitize(flag_input)

        if safe_flags is None:
            print("[!] Invalid flags.")
            return

        try:
            flags = shlex.split(safe_flags)
        except ValueError:
            print("[!] Invalid flags.")
            return
    else:
        flags = list(default_flags)

    timeout_input = input(f"Timeout seconds (default {timeout}): ").strip()

    if timeout_input:
        if timeout_input.isdigit():
            timeout = int(timeout_input)
        else:
            print("[!] Invalid timeout. Using default.")

    if binary == "masscan":
        print("[*] Masscan note: full-port /24 scans can take hours.")
        print("[*] Use common ports for quick lab scans, or increase timeout.")

    cmd = [binary] + flags

    if needs_target:
        cmd.append(target)

    print(f"\n[*] Running: {' '.join(cmd)}")
    print(f"[*] Timeout: {timeout}s\n")

    user_id = get_user_id(username)

    output, rc = run_command(cmd, timeout)
    status = "completed" if rc == 0 else "failed"

    scan_id = save_scan(
        user_id,
        name,
        target,
        " ".join(flags),
        output,
        status,
        team,
    )

    display = output[:3000]
    if display:
        print(display)

    if len(output) > 3000:
        print(f"\n... [truncated - full output saved, {len(output)} chars total]")

    if status == "completed":
        print(f"\n[+] {name} completed. Results saved as scan #{scan_id}.")
    else:
        print(f"\n[!] {name} failed. Results saved as scan #{scan_id}.")
