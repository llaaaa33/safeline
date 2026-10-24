"""SafeLine backend: Vapi webhook, dashboard state, resolve endpoint, dashboard page.

Run: uvicorn app.main:app --port 8000
"""
import json
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app import db, notify, vapi

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("safeline")

SEED: dict = {}
SEVERITIES = {"low", "medium", "high"}
_seen_tool_calls: set[str] = set()
_public_base = ""
_live_call: dict = {}  # most recent inbound call: id, caller, status


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global SEED
    db.init_db()
    SEED = db.load_seed()
    log.info("Loaded %s: %d zones, %d workers", SEED["_path"], len(SEED["zones"]), len(SEED["workers"]))
    yield


app = FastAPI(title="SafeLine", lifespan=lifespan)


# ---------- roster helpers ----------

def _digits(phone: str | None) -> str:
    d = "".join(c for c in (phone or "") if c.isdigit())
    return d[-10:] if len(d) >= 10 else ""  # placeholders like +1XXXXXXXXXX never match


def find_worker(phone: str | None) -> dict | None:
    d = _digits(phone)
    return next((w for w in SEED["workers"] if d and _digits(w["phone"]) == d), None)


def caller_for(number: str | None) -> dict:
    return find_worker(number) or {"name": "Unknown caller", "language": "en", "phone": number or ""}


def zone_name(zone_id: str | None) -> str:
    z = next((z for z in SEED["zones"] if z["id"] == zone_id), None)
    return z["name"] if z else "Unknown zone"


def webhook_url(request: Request | None = None) -> str:
    """Use the host Vapi reached us on (the tunnel), so a stale PUBLIC_BASE_URL can't break tools."""
    global _public_base
    if request is not None:
        host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
        if host and not host.startswith(("localhost", "127.0.0.1", "[::1]")):
            _public_base = f"{request.headers.get('x-forwarded-proto', 'https')}://{host}"
    base = _public_base or os.getenv("PUBLIC_BASE_URL", "").strip() or "http://localhost:8000"
    return base.rstrip("/") + "/vapi/webhook"


# ---------- manager alert (after the tool result is sent) ----------

async def alert_manager(hazard_id: int, discord_alert_id: int) -> None:
    hazard = db.get_hazard(hazard_id)
    zname = zone_name(hazard["zone_id"])
    if hazard["is_emergency"]:
        ok = await notify.send_discord(notify.format_emergency(hazard, zname), urgent=True)
    else:
        ok = await notify.send_discord(notify.format_hazard(hazard, zname))
    db.update_alert(discord_alert_id, status={True: "delivered", False: "failed", None: "skipped"}[ok])


# ---------- tool handlers (must return fast) ----------

def _args(tool_call: dict) -> dict:
    args = tool_call.get("function", {}).get("arguments") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {}
    return args


def handle_report_hazard(args: dict, call: dict, caller: dict, tasks: BackgroundTasks) -> dict:
    zone_ids = {z["id"] for z in SEED["zones"]}
    zone_id = str(args.get("zone_id", "")).strip().upper()
    if zone_id not in zone_ids:
        return {"ok": False, "error": f"Unknown zone. Ask the caller which zone: {', '.join(sorted(zone_ids))}."}
    severity = str(args.get("severity", "medium")).lower()
    hazard_id = db.insert_hazard(
        call_id=call.get("id"), caller_phone=caller["phone"], caller_name=caller["name"], zone_id=zone_id,
        hazard_type=str(args.get("hazard_type") or "unspecified hazard"),
        severity=severity if severity in SEVERITIES else "medium",
        description_original=str(args.get("description_original") or ""),
        description_en=str(args.get("description_en") or ""), language=caller["language"],
    )
    discord_alert_id = db.insert_alert(hazard_id=hazard_id, recipient_name="Safety manager", phone="",
                                       language="en", channel="discord")
    tasks.add_task(alert_manager, hazard_id, discord_alert_id)
    return {"ok": True, "safety_manager_alerted": True}


def handle_report_emergency(args: dict, call: dict, caller: dict, tasks: BackgroundTasks) -> dict:
    zone_id = str(args.get("zone_id", "")).strip().upper()
    if zone_id not in {z["id"] for z in SEED["zones"]}:
        zone_id = "unknown"
    hazard_id = db.insert_hazard(
        call_id=call.get("id"), caller_phone=caller["phone"], caller_name=caller["name"], zone_id=zone_id,
        hazard_type="EMERGENCY", severity="high",
        description_original=str(args.get("description_original") or ""),
        description_en=str(args.get("description_en") or ""), language=caller["language"], is_emergency=True,
    )
    discord_alert_id = db.insert_alert(hazard_id=hazard_id, recipient_name="Safety manager (@here)", phone="",
                                       language="en", channel="discord")
    tasks.add_task(alert_manager, hazard_id, discord_alert_id)
    return {"ok": True, "safety_manager_alerted": True,
            "say_to_caller": "Help is on the way. Stay where you are if it is safe."}


def handle_check_zone(args: dict, call: dict, caller: dict, tasks: BackgroundTasks) -> dict:
    zone_ids = {z["id"] for z in SEED["zones"]}
    zone_id = str(args.get("zone_id", "all")).strip().upper()
    zone_id = zone_id if zone_id in zone_ids else None
    hazards = db.open_hazards(zone_id)
    return {
        "scope": zone_name(zone_id) if zone_id else "whole site",
        "open_hazards": len(hazards),
        "details": [
            {"zone": zone_name(h["zone_id"]), "severity": h["severity"], "reported_at": h["created_at"][11:16],
             "hazard": f"EMERGENCY: {h['description_en']}" if h["is_emergency"] else h["hazard_type"]}
            for h in hazards[:5]
        ],
    }


TOOL_HANDLERS = {"report_hazard": handle_report_hazard, "report_emergency": handle_report_emergency,
                 "check_zone": handle_check_zone}


# ---------- routes ----------

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request, tasks: BackgroundTasks):
    body = await request.json()
    msg = body.get("message", {})
    mtype = msg.get("type", "")
    call = msg.get("call") or {}
    number = (call.get("customer") or msg.get("customer") or {}).get("number")
    log.info("webhook %s: %s", mtype, json.dumps(body, ensure_ascii=False)[:400])

    if mtype == "assistant-request":
        worker = caller_for(number)
        log.info("Inbound call from %s -> %s (%s)", number, worker["name"], worker["language"])
        _live_call.update(id=call.get("id"), caller=worker["name"], status="ringing")
        return {"assistant": vapi.build_inbound_assistant(worker, SEED["zones"], webhook_url(request))}

    if mtype == "tool-calls":
        caller = caller_for(number)
        results = []
        for tc in msg.get("toolCallList", []):
            tc_id, name = tc.get("id"), tc.get("function", {}).get("name")
            handler = TOOL_HANDLERS.get(name)
            if handler is None:
                results.append({"name": name, "toolCallId": tc_id, "error": f"unknown tool {name}"})
                continue
            if tc_id in _seen_tool_calls:
                out = {"ok": True, "note": "already recorded"}
            else:
                _seen_tool_calls.add(tc_id)
                out = handler(_args(tc), call, caller, tasks)
            results.append({"name": name, "toolCallId": tc_id, "result": json.dumps(out, ensure_ascii=False)})
        return {"results": results}

    if mtype == "conversation-update":
        roles = {"user": "user", "bot": "assistant", "assistant": "assistant"}
        merged: list[tuple[str, str]] = []  # Vapi splits one turn into fragments; show one line per turn
        for m in msg.get("messages") or []:
            role, text = roles.get(m.get("role")), (m.get("message") or m.get("content") or "").strip()
            if not role or not text:
                continue
            if merged and merged[-1][0] == role:
                merged[-1] = (role, f"{merged[-1][1]} {text}")
            else:
                merged.append((role, text))
        if merged:
            db.replace_transcript(call.get("id", "unknown"), merged)
        return {}

    if mtype.startswith("transcript"):
        final = mtype != "transcript" or msg.get("transcriptType") == "final"
        if final and msg.get("transcript"):
            db.add_transcript(call.get("id", "unknown"), msg.get("role", "user"), msg["transcript"])
        return {}

    if mtype in ("status-update", "end-of-call-report") and call.get("id") == _live_call.get("id"):
        _live_call["status"] = "ended" if mtype == "end-of-call-report" else msg.get("status")
    return {}


class ResolveBody(BaseModel):
    resolved: bool = True


@app.post("/api/hazards/{hazard_id}/resolve")
def resolve_hazard(hazard_id: int, body: ResolveBody):
    if not db.get_hazard(hazard_id):
        raise HTTPException(404, "hazard not found")
    db.set_resolved(hazard_id, body.resolved)
    return {"ok": True, "hazard": db.get_hazard(hazard_id)}


@app.get("/api/state")
def api_state():
    state = db.get_state()
    for h in state["hazards"]:
        h["zone_name"] = zone_name(h["zone_id"])
    open_by_zone = db.open_counts_by_zone()
    state["zones"] = [
        {"id": z["id"], "name": z["name"], "open": open_by_zone.get(z["id"], {}).get("open", 0),
         "emergency": bool(open_by_zone.get(z["id"], {}).get("emergency"))}
        for z in SEED["zones"]
    ]
    state["live_call"] = dict(_live_call)
    return state


@app.get("/")
def dashboard():
    return FileResponse(db.ROOT / "static" / "dashboard.html")
