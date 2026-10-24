"""SQLite schema, roster loading and queries."""
import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "safeline.db"

_conn: sqlite3.Connection | None = None
_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS hazards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    call_id TEXT,
    caller_phone TEXT,
    caller_name TEXT,
    zone_id TEXT,
    hazard_type TEXT,
    severity TEXT,
    description_original TEXT,
    description_en TEXT,
    language TEXT,
    is_emergency INTEGER NOT NULL DEFAULT 0,
    resolved_at TEXT          -- set when the safety manager ticks "resolved"
);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hazard_id INTEGER NOT NULL REFERENCES hazards(id),
    recipient_name TEXT,
    phone TEXT,
    language TEXT,
    message TEXT,
    channel TEXT NOT NULL,   -- discord
    status TEXT NOT NULL,    -- queued | calling | delivered | failed
    vapi_call_id TEXT,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id TEXT,
    role TEXT,
    text TEXT,
    ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_alerts_call ON alerts(vapi_call_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_call ON transcripts(call_id);
"""


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def load_seed() -> dict:
    """seed.local.json (gitignored, real phone numbers) wins over seed.json."""
    local = ROOT / "seed.local.json"
    path = local if local.exists() else ROOT / "seed.json"
    seed = json.loads(path.read_text(encoding="utf-8"))
    seed["_path"] = path.name
    return seed


def init_db(path: Path | None = None) -> None:
    global _conn
    _conn = sqlite3.connect(path or DB_PATH, check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    _conn.executescript(SCHEMA)
    columns = {r["name"] for r in _conn.execute("PRAGMA table_info(hazards)")}
    if "resolved_at" not in columns:  # databases created before the resolve feature
        _conn.execute("ALTER TABLE hazards ADD COLUMN resolved_at TEXT")
    _conn.commit()


def _exec(sql: str, params: tuple = ()) -> int:
    with _lock:
        cur = _conn.execute(sql, params)
        _conn.commit()
        return cur.lastrowid


def _query(sql: str, params: tuple = ()) -> list[dict]:
    with _lock:
        return [dict(r) for r in _conn.execute(sql, params).fetchall()]


def insert_hazard(*, call_id, caller_phone, caller_name, zone_id, hazard_type, severity,
                  description_original, description_en, language, is_emergency=False) -> int:
    return _exec(
        "INSERT INTO hazards (created_at, call_id, caller_phone, caller_name, zone_id, hazard_type, severity,"
        " description_original, description_en, language, is_emergency) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (now(), call_id, caller_phone, caller_name, zone_id, hazard_type, severity,
         description_original, description_en, language, int(is_emergency)),
    )


def get_hazard(hazard_id: int) -> dict | None:
    rows = _query("SELECT * FROM hazards WHERE id = ?", (hazard_id,))
    return rows[0] if rows else None


def insert_alert(*, hazard_id, recipient_name, phone, language, channel, message="", status="queued") -> int:
    return _exec(
        "INSERT INTO alerts (hazard_id, recipient_name, phone, language, message, channel, status, updated_at)"
        " VALUES (?,?,?,?,?,?,?,?)",
        (hazard_id, recipient_name, phone, language, message, channel, status, now()),
    )


def update_alert(alert_id: int, *, status: str) -> None:
    _exec("UPDATE alerts SET status = ?, updated_at = ? WHERE id = ?", (status, now(), alert_id))


def set_resolved(hazard_id: int, resolved: bool) -> None:
    _exec("UPDATE hazards SET resolved_at = ? WHERE id = ?", (now() if resolved else None, hazard_id))


def open_hazards(zone_id: str | None = None) -> list[dict]:
    if zone_id:
        return _query("SELECT * FROM hazards WHERE resolved_at IS NULL AND zone_id = ? ORDER BY id DESC", (zone_id,))
    return _query("SELECT * FROM hazards WHERE resolved_at IS NULL ORDER BY id DESC")


def open_counts_by_zone() -> dict[str, dict]:
    rows = _query("SELECT zone_id, COUNT(*) AS open, MAX(is_emergency) AS emergency FROM hazards"
                  " WHERE resolved_at IS NULL GROUP BY zone_id")
    return {r["zone_id"]: r for r in rows}


def add_transcript(call_id: str, role: str, text: str) -> None:
    _exec("INSERT INTO transcripts (call_id, role, text, ts) VALUES (?,?,?,?)", (call_id, role, text, now()))


def replace_transcript(call_id: str, lines: list[tuple[str, str]]) -> None:
    """Replace a call's transcript with the full conversation so far (idempotent)."""
    ts = now()
    with _lock:
        _conn.execute("DELETE FROM transcripts WHERE call_id = ?", (call_id,))
        _conn.executemany("INSERT INTO transcripts (call_id, role, text, ts) VALUES (?,?,?,?)",
                          [(call_id, role, text, ts) for role, text in lines])
        _conn.commit()


def get_state() -> dict:
    # open hazards first (newest on top), then resolved ones; `notified` = Discord delivery status
    hazards = _query(
        "SELECT h.*, (SELECT a.status FROM alerts a WHERE a.hazard_id = h.id ORDER BY a.id DESC LIMIT 1) AS notified"
        " FROM hazards h ORDER BY (h.resolved_at IS NOT NULL), h.id DESC LIMIT 30"
    )
    latest = _query("SELECT call_id FROM transcripts ORDER BY id DESC LIMIT 1")
    transcript = []
    if latest:
        transcript = _query(
            "SELECT * FROM (SELECT * FROM transcripts WHERE call_id = ? ORDER BY id DESC LIMIT 30) ORDER BY id",
            (latest[0]["call_id"],),
        )
    return {"hazards": hazards, "transcript": transcript}
