# SafeLine — a voice safety network for construction sites

**c0mpiled-16 @ UCSD · Track: No App**

A worker reports a hazard by **phone call in their own language**. SafeLine logs it, alerts the safety manager in English, and **immediately calls the other workers in that zone** with a spoken warning in each worker's language. Workers never look at a screen — the only screen is the safety manager's dashboard.

In the real product each worker wears a cellular earpiece that dials SafeLine with one button and auto-answers alerts. SafeLine only sees phone calls, so the backend is identical whether the worker uses a phone, an earpiece, or a smart hard hat.

## How it works

```
Worker's phone / earpiece ──► Vapi (phone number, speech-to-text, LLM, text-to-speech)
                                 │  webhooks: assistant-request, tool-calls, transcript, status
                                 ▼
                           FastAPI backend ──► SQLite
                                 ├──► Discord webhook (manager alerts, 🚨 @here for emergencies)
                                 ├──► LLM (translates the warning into each worker's language)
                                 └──► Vapi outbound calls (warns every other worker in the zone)
                           Manager dashboard (polls /api/state every 1.5 s)
```

1. **Inbound call** → Vapi asks the backend for an assistant (`assistant-request`). The backend looks up the caller in the roster and returns an assistant that listens and speaks in that worker's language (English, Chinese, Spanish).
2. The assistant calls `report_hazard` (zone, hazard, severity, original words, English translation) or `report_emergency`. The backend stores it and answers immediately; Discord and phone calls run in the background.
3. **Closed loop**: every other worker in that zone gets a phone call with the warning in their language. The dashboard tracks each call: calling → delivered / failed.
4. **Emergency**: Discord `🚨 URGENT @here`, a red banner with an alarm on the manager's dashboard, and optionally a call to the supervisor.

| File | Purpose |
|---|---|
| `app/main.py` | Vapi webhook, `/api/state`, dashboard |
| `app/vapi.py` | Per-caller inbound assistant, outbound alert assistant, call helper |
| `app/db.py` | SQLite schema + queries, roster loading |
| `app/llm.py` | Alert translation |
| `app/notify.py` | Discord alerts (`python -m app.notify` = test message) |
| `static/dashboard.html` | Projector view for the safety manager |
| `scripts/simulate_tool_call.py` | Fake calls for testing without phones |
| `scripts/configure_vapi_number.py` | Point the Vapi number at this backend |

## Run it

Needs: Vapi account + API key, a Twilio number imported into Vapi (free Vapi numbers can't call out), a Discord webhook, an OpenAI or Anthropic key, ngrok.

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # fill it in
copy seed.json seed.local.json    # real E.164 numbers for the roster
uvicorn app.main:app --port 8000
ngrok http 8000                   # put the https URL in PUBLIC_BASE_URL
python scripts/configure_vapi_number.py
python -m app.notify              # Discord test
```

Dashboard: http://localhost:8000 (click it once so the alarm sound is allowed).

## Test without phones

```bash
python scripts/simulate_tool_call.py             # Chinese report, zone B
python scripts/simulate_tool_call.py emergency   # fall from a ladder, zone A
python scripts/simulate_tool_call.py assistant   # assistant config for the presenter
```

Design choices: [NOTES.md](NOTES.md).
