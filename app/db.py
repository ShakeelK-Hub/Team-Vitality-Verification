"""
Local data layer for the Vitality check-in app.
Everything runs against a local SQLite file so the app works with
zero internet connectivity. Excel import replaces the member cache;
a sync step (added later) can push/pull this over a network when available.
"""

import sqlite3
import re
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".vitality_checkin" / "local.db"


def _normalise_id(raw: str) -> str:
    """Strip whitespace and non-alphanumeric noise from a scanned/typed ID."""
    return re.sub(r"[^A-Za-z0-9]", "", str(raw or "")).strip().upper()


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS members (
            id_number   TEXT PRIMARY KEY,
            full_name   TEXT,
            extra_json  TEXT,
            imported_at TEXT
        );

        CREATE TABLE IF NOT EXISTS checkins (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            id_number   TEXT,
            full_name   TEXT,
            result      TEXT,        -- 'granted' or 'denied'
            timestamp   TEXT,
            synced      INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def replace_members(rows: list[dict]) -> int:
    """
    Wipes and reloads the members table from a freshly imported Excel sheet.
    rows: list of dicts with keys 'id_number', 'full_name'.
    Returns the number of rows loaded.
    """
    conn = get_connection()
    now = datetime.now().isoformat(timespec="seconds")
    with conn:
        conn.execute("DELETE FROM members")
        conn.executemany(
            "INSERT OR REPLACE INTO members (id_number, full_name, imported_at) "
            "VALUES (?, ?, ?)",
            [
                (_normalise_id(r["id_number"]), r.get("full_name", ""), now)
                for r in rows
                if r.get("id_number")
            ],
        )
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('last_import', ?)", (now,)
        )
    count = conn.execute("SELECT COUNT(*) c FROM members").fetchone()["c"]
    conn.close()
    return count


def member_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) c FROM members").fetchone()
    conn.close()
    return row["c"] if row else 0


def last_import_time() -> str | None:
    conn = get_connection()
    row = conn.execute("SELECT value FROM meta WHERE key = 'last_import'").fetchone()
    conn.close()
    return row["value"] if row else None


def lookup_member(raw_id: str) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM members WHERE id_number = ?", (_normalise_id(raw_id),)
    ).fetchone()
    conn.close()
    return row


def log_checkin(id_number: str, full_name: str, result: str) -> None:
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO checkins (id_number, full_name, result, timestamp) VALUES (?, ?, ?, ?)",
            (_normalise_id(id_number), full_name, result, datetime.now().isoformat(timespec="seconds")),
        )
    conn.close()


def recent_checkins(limit: int = 25) -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM checkins ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return rows


def all_checkins() -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM checkins ORDER BY id ASC").fetchall()
    conn.close()
    return rows

def set_meta(key: str, value: str) -> None:
    """Generic settings store — used for things like the chosen background image path."""
    conn = get_connection()
    with conn:
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, value))
    conn.close()


def get_meta(key: str) -> str | None:
    conn = get_connection()
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None