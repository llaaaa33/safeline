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
    is_emergency INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hazard_id INTEGER NOT NULL REFERENCES hazards(id),
    recipient_name TEXT,
    phone TEXT,
    language TEXT,
    message TEXT,
    channel TEXT NOT NULL,   -- call | discord
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


def update_alert(alert_id: int, *, status: str | None = None, message: str | None = None,
                 vapi_call_id: str | None = None) -> None:
    sets, params = ["updated_at = ?"], [now()]
    for col, val in (("status", status), ("message", message), ("vapi_call_id", vapi_call_id)):
        if val is not None:
            sets.append(f"{col} = ?")
            params.append(val)
    params.append(alert_id)
    _exec(f"UPDATE alerts SET {', '.join(sets)} WHERE id = ?", tuple(params))


def get_alert_by_call(vapi_call_id: str) -> dict | None:
    rows = _query("SELECT * FROM alerts WHERE vapi_call_id = ?", (vapi_call_id,))
    return rows[0] if rows else None


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
    hazards = _query("SELECT * FROM hazards ORDER BY id DESC LIMIT 20")
    alerts = _query(
        "SELECT a.*, h.zone_id, h.hazard_type, h.is_emergency FROM alerts a"
        " JOIN hazards h ON h.id = a.hazard_id ORDER BY a.id DESC LIMIT 20"
    )
    latest = _query("SELECT call_id FROM transcripts ORDER BY id DESC LIMIT 1")
    transcript = []
    if latest:
        transcript = _query(
            "SELECT * FROM (SELECT * FROM transcripts WHERE call_id = ? ORDER BY id DESC LIMIT 30) ORDER BY id",
            (latest[0]["call_id"],),
        )
    return {"hazards": hazards, "alerts": alerts, "transcript": transcript}
