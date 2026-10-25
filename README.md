# SafeLine

**A hands-free voice safety device for construction workers.** c0mpiled-16 @ UCSD · Track: No App

SafeLine works like the walkie-talkie a worker already carries: press once and talk, in their own language, hands still on the job. But there is no noisy shared channel — the worker is talking to an AI agent that:

- **logs hazards** — "There's a loose plank on the level 3 scaffold in Zone B." The agent asks one follow-up only if something is missing, then confirms the safety manager has been alerted;
- **answers questions** — "Is Zone B safe right now?" It reads the open hazards back from live site data;
- **handles emergencies** — "Help, someone fell off a ladder!" It says help is on the way and raises an alarm.

Workers never look at a screen. The only screen belongs to the safety manager: a live dashboard with the conversation as it happens, a hazard feed with the worker's own words, and a zone board (Clear / Open / Emergency). The manager checks each hazard off when it is fixed.

**Alerts:** every new report plays a chime on the dashboard and posts to Discord. An emergency adds a full-width red banner with a siren, turns its zone red, and sends a Discord `@here`.

**This repository is the software behind the device.** In the prototype, a phone call stands in for the device; the agent, backend and dashboard are the same either way.

## How it works

```
Worker's device (prototype: a phone call) ──► Vapi (voice, speech-to-text, LLM, text-to-speech)
                                                 │  webhooks
                                                 ▼
                                           FastAPI backend ──► SQLite
                                                 ├──► Discord (manager alerts, @here for emergencies)
                                                 └──► Manager dashboard (live, polls every 1.5 s)
```

- For each conversation the backend looks the worker up in the site roster and returns an agent that listens and speaks in that worker's language (English, Chinese, Spanish).
- The agent calls three tools: `report_hazard`, `report_emergency`, `check_zone`.
- The manager resolves hazards from the dashboard (`POST /api/hazards/{id}/resolve`); a zone turns green when nothing in it is open.

| Path | Purpose |
|---|---|
| `app/main.py` | Vapi webhook, tool handlers, `/api/state`, resolve endpoint, dashboard |
| `app/vapi.py` | Agent configuration (prompt, tools, speech-to-text, voice) |
| `app/db.py` | SQLite schema and queries, site roster |
| `app/notify.py` | Discord alerts |
| `static/dashboard.html` | Safety manager dashboard |
| `scripts/simulate_tool_call.py` | Fake conversations for testing without a device |
| `scripts/configure_vapi_number.py` | Points the Vapi number at this backend |

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # Vapi key, Discord webhook (optional), tunnel URL
copy seed.json seed.local.json    # zones and workers
uvicorn app.main:app --port 8000
cloudflared tunnel --protocol http2 --url http://localhost:8000   # put the https URL in PUBLIC_BASE_URL
python scripts/configure_vapi_number.py
```

Dashboard: http://localhost:8000

Without a device: `python scripts/simulate_tool_call.py` (hazard report) or `python scripts/simulate_tool_call.py emergency`.

## How I used AI

I used AI (Claude Code) to write the code.
