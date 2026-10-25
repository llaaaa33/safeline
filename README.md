# SafeLine — a hands-free voice safety device for construction workers

**c0mpiled-16 @ UCSD · Track: No App**

SafeLine works like the walkie-talkie a worker already carries: **press once and talk**, in their own language, hands still on the job. But there is no noisy shared channel — the worker is talking to an AI agent that logs the hazard, **alerts the safety manager in seconds** (live dashboard with an alarm for emergencies, plus Discord), and **answers questions** like "Is Zone B safe right now?" from live site data. Workers never look at a screen; the only screen belongs to the manager, who ticks each hazard off when it is fixed.

**This repo is the software behind the device.** In the prototype a phone call stands in for the device: the agent, backend and dashboard are the same whether the voice comes from a phone or a wearable radio.

## How it works

```
Worker's device (prototype: a phone call) ──► Vapi (voice connection, speech-to-text, LLM, text-to-speech)
                                 │  webhooks: assistant-request, tool-calls, conversation-update, status
                                 ▼
                           FastAPI backend ──► SQLite
                                 ├──► Discord webhook (manager alert, 🚨 @here for emergencies)
                                 └──► Manager dashboard (polls /api/state every 1.5 s)
```

1. **Inbound call** → Vapi asks the backend for an assistant (`assistant-request`). The backend looks the caller up in the site roster and returns an assistant that listens and speaks in that worker's language (English, Chinese, Spanish).
2. The assistant calls `report_hazard` (zone, hazard, severity, the worker's words, English translation), `report_emergency`, or `check_zone` (reads open hazards back to the worker). The backend stores reports, answers instantly, and posts to Discord in the background.
3. **Dashboard**: live call captions, hazard feed, and a zone board (Clear / N open / Emergency). Emergencies raise a red banner and a siren.
4. **Resolve**: the manager ticks *Mark resolved* on a hazard; it moves to the resolved list and its zone turns green once nothing is open.

| File | Purpose |
|---|---|
| `app/main.py` | Vapi webhook, `/api/state`, `POST /api/hazards/{id}/resolve`, dashboard |
| `app/vapi.py` | Per-caller assistant config (prompt, tools, transcriber, voice) |
| `app/db.py` | SQLite schema + queries, roster loading |
| `app/notify.py` | Discord alerts (`python -m app.notify` = test message) |
| `static/dashboard.html` | Manager dashboard (projector layout) |
| `scripts/simulate_tool_call.py` | Fake calls for testing without a phone |
| `scripts/configure_vapi_number.py` | Point the Vapi number at this backend |

## Run it

Needs: a Vapi account + API key + phone number (a free Vapi number is enough — calls only come in), a Discord webhook (optional), and a tunnel (cloudflared).

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # fill it in
copy seed.json seed.local.json    # real E.164 numbers for the roster
uvicorn app.main:app --port 8000
cloudflared tunnel --protocol http2 --url http://localhost:8000   # put the https URL in PUBLIC_BASE_URL
python scripts/configure_vapi_number.py
```

Dashboard: http://localhost:8000 — click it once so the browser allows the alarm sound.

## Test without a phone

```bash
python scripts/simulate_tool_call.py             # hazard report, zone B
python scripts/simulate_tool_call.py emergency   # fall from a ladder, zone A
python scripts/simulate_tool_call.py assistant   # assistant config for the presenter
```

Design choices: [NOTES.md](NOTES.md).
