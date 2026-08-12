"""Record tool executions for lab accountability."""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

log = logging.getLogger("cyberlab.audit")
DATABASE = Path("database/database.db")


def log_tool_use(
    username: str,
    role: str,
    team: str,
    tool_name: str,
    status: str = "ok",
) -> None:
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute(
                """
                INSERT INTO tool_usage(username, role, team, tool_name, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, role, team, tool_name, status),
            )
    except sqlite3.Error as exc:
        log.warning("Could not record tool usage: %s", exc)


def recent_usage(limit: int = 20) -> list[tuple]:
    if not DATABASE.exists():
        return []

    with sqlite3.connect(DATABASE) as conn:
        return conn.execute(
            """
            SELECT created_at, username, role, team, tool_name, status
            FROM tool_usage
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def usage_summary() -> list[tuple]:
    if not DATABASE.exists():
        return []

    with sqlite3.connect(DATABASE) as conn:
        return conn.execute(
            """
            SELECT team, tool_name, COUNT(*) AS uses
            FROM tool_usage
            GROUP BY team, tool_name
            ORDER BY uses DESC, team, tool_name
            """
        ).fetchall()
