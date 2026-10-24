"""SafeLine backend: Vapi webhook, dashboard state, dashboard page.

Run: uvicorn app.main:app --port 8000
"""
import json
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import FileResponse

from app import db, llm, notify, vapi

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("safeline")

SEED: dict = {}
SEVERITIES = {"low", "medium", "high"}
_seen_tool_calls: set[str] = set()
_public_base = ""


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
    return z["name"] if z else "an unknown zone"


def webhook_url(request: Request | None = None) -> str:
    """Use the host Vapi reached us on (the tunnel), so a stale PUBLIC_BASE_URL can't break tools."""
    global _public_base
    if request is not None:
        host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
        if host and not host.startswith(("localhost", "127.0.0.1", "[::1]")):
            _public_base = f"{request.headers.get('x-forwarded-proto', 'https')}://{host}"
    base = _public_base or os.getenv("PUBLIC_BASE_URL", "").strip() or "http://localhost:8000"
    return base.rstrip("/") + "/vapi/webhook"


# ---------- background work (after the tool result is sent) ----------

async def _call(alert_id: int, phone: str, assistant: dict, who: str) -> None:
    call_id, err = await vapi.create_outbound_call(phone, assistant)
    if call_id:
        db.update_alert(alert_id, status="calling", vapi_call_id=call_id)
    else:
        log.error("Alert call to %s failed: %s", who, err)
        db.update_alert(alert_id, status="failed")


async def dispatch_hazard(hazard_id: int, recipients: list[tuple[int, dict]], discord_alert_id: int, base_url: str):
    hazard = db.get_hazard(hazard_id)
    zname = zone_name(hazard["zone_id"])
    ok = await notify.send_discord(notify.format_hazard(hazard, zname, [w["name"] for _, w in recipients]))
    db.update_alert(discord_alert_id, status="delivered" if ok else "failed")

    for alert_id, worker in recipients:
        message = await llm.translate_alert(zname, hazard["hazard_type"], hazard["description_en"], worker["language"])
        db.update_alert(alert_id, message=message)
        assistant = vapi.build_alert_assistant(
            message=message, language=worker["language"], zone_name=zname, hazard_type=hazard["hazard_type"],
            description_en=hazard["description_en"], webhook_url=base_url,
        )
        await _call(alert_id, worker["phone"], assistant, worker["name"])


async def dispatch_emergency(hazard_id: int, call_alert_id: int | None, discord_alert_id: int, base_url: str):
    hazard = db.get_hazard(hazard_id)
    zname = zone_name(hazard["zone_id"])
    supervisor = os.getenv("SUPERVISOR_PHONE", "").strip()
    ok = await notify.send_discord(notify.format_emergency(hazard, zname, supervisor), urgent=True)
    db.update_alert(discord_alert_id, status="delivered" if ok else "failed")

    if call_alert_id is not None:
        message = f"Emergency reported in {zname}: {hazard['description_en']}"
        db.update_alert(call_alert_id, message=message)
        assistant = vapi.build_alert_assistant(
            message=message, language="en", zone_name=zname, hazard_type="EMERGENCY",
            description_en=hazard["description_en"], webhook_url=base_url,
        )
        await _call(call_alert_id, supervisor, assistant, "supervisor")


# ---------- tool handlers (must return fast) ----------

def _args(tool_call: dict) -> dict:
    args = tool_call.get("function", {}).get("arguments") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {}
    return args


def handle_report_hazard(args: dict, call: dict, caller: dict, tasks: BackgroundTasks, base_url: str) -> dict:
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
    workers = [w for w in SEED["workers"] if w["zone"] == zone_id and _digits(w["phone"]) != _digits(caller["phone"])]
    recipients = [(db.insert_alert(hazard_id=hazard_id, recipient_name=w["name"], phone=w["phone"],
                                   language=w["language"], channel="call"), w) for w in workers]
    discord_alert_id = db.insert_alert(hazard_id=hazard_id, recipient_name="Safety manager", phone="",
                                       language="en", channel="discord")
    tasks.add_task(dispatch_hazard, hazard_id, recipients, discord_alert_id, base_url)
    return {"ok": True, "coworkers_alerted": len(workers)}


def handle_report_emergency(args: dict, call: dict, caller: dict, tasks: BackgroundTasks, base_url: str) -> dict:
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
    supervisor = os.getenv("SUPERVISOR_PHONE", "").strip()
    call_alert_id = None
    if supervisor:
        sup = find_worker(supervisor)
        call_alert_id = db.insert_alert(hazard_id=hazard_id, phone=supervisor, language="en", channel="call",
                                        recipient_name=f"Supervisor ({sup['name']})" if sup else "Supervisor")
    tasks.add_task(dispatch_emergency, hazard_id, call_alert_id, discord_alert_id, base_url)
    return {"ok": True, "manager_alerted": True,
            "say_to_caller": "Help is on the way. Stay where you are if it is safe."}


TOOL_HANDLERS = {"report_hazard": handle_report_hazard, "report_emergency": handle_report_emergency}


# ---------- outbound alert call status ----------

def handle_status(call: dict, status: str | None, ended_reason: str | None = None) -> None:
    alert = db.get_alert_by_call(call.get("id", ""))
    if not alert or alert["status"] == "delivered":
        return
    if status in ("queued", "ringing"):
        db.update_alert(alert["id"], status="calling")
    elif status == "in-progress":
        db.update_alert(alert["id"], status="delivered")  # answered: the worker is hearing the alert
    elif status == "ended":
        log.info("Alert call %s ended before it was answered: %s", call.get("id"), ended_reason or call.get("endedReason"))
        db.update_alert(alert["id"], status="failed")


# ---------- routes ----------

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request, tasks: BackgroundTasks):
    body = await request.json()
    msg = body.get("message", {})
    mtype = msg.get("type", "")
    call = msg.get("call") or {}
    number = (call.get("customer") or msg.get("customer") or {}).get("number")
    log.info("webhook %s: %s", mtype, json.dumps(body, ensure_ascii=False)[:400])
    base_url = webhook_url(request)

    if mtype == "assistant-request":
        worker = caller_for(number)
        log.info("Inbound call from %s -> %s (%s)", number, worker["name"], worker["language"])
        return {"assistant": vapi.build_inbound_assistant(worker, SEED["zones"], base_url)}

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
                out = handler(_args(tc), call, caller, tasks, base_url)
            results.append({"name": name, "toolCallId": tc_id, "result": json.dumps(out, ensure_ascii=False)})
        return {"results": results}

    if mtype == "conversation-update":
        roles = {"user": "user", "bot": "assistant", "assistant": "assistant"}
        lines = [(roles[m["role"]], (m.get("message") or m.get("content") or "").strip())
                 for m in msg.get("messages") or [] if m.get("role") in roles]
        lines = [(role, text) for role, text in lines if text]
        if lines:
            db.replace_transcript(call.get("id", "unknown"), lines)
        return {}

    if mtype.startswith("transcript"):
        final = mtype != "transcript" or msg.get("transcriptType") == "final"
        if final and msg.get("transcript"):
            db.add_transcript(call.get("id", "unknown"), msg.get("role", "user"), msg["transcript"])
        return {}

    if mtype == "status-update":
        handle_status(call, msg.get("status"))
    elif mtype == "end-of-call-report":
        handle_status(call, "ended", msg.get("endedReason"))
    return {}


@app.get("/api/state")
def api_state():
    state = db.get_state()
    for row in state["hazards"] + state["alerts"]:
        row["zone_name"] = zone_name(row["zone_id"])
    return state


@app.get("/")
def dashboard():
    return FileResponse(db.ROOT / "static" / "dashboard.html")
