# SafeLine — submission draft

**Track:** No App
**Video:** _(link)_ · **Code:** _(link)_

## Form: 2 Sentence Description of the Project

SafeLine is a no-interface safety line for construction workers: they report a hazard just by calling and talking in their own language — no app, no screen, hands stay on the job. An AI voice agent logs it in seconds and alerts the safety manager on a live site dashboard and Discord, with emergencies raising an alarm and every hazard tracked by zone until it is marked resolved.

## One line
Workers report hazards by voice; the safety manager sees and closes them on one live screen.

## The problem
On a construction site the people who first see a hazard — a loose plank, an open edge, a leaking line — are wearing gloves, standing on ladders, working in noise, and often speak different languages. Safety apps assume someone will stop, take out a phone, unlock it and type. In practice the report travels by shouting, or not at all, and the safety manager hears about it hours later, if ever.

## What the worker experiences (no interface)
1. **Report by voice.** "Hey Siri, call Safe Line." The worker describes the hazard in their own words and language. Safe Line asks one follow-up only if the zone or hazard is unclear, then confirms the safety manager has been alerted. Hands stay on the job; the phone stays in the pocket.
2. **Emergency by voice.** "Help, someone fell off a ladder!" Safe Line immediately says help is on the way and raises an urgent alert.

## What the safety manager sees
- A live dashboard: the call as it happens (captions), the hazard feed with the worker's own words and an English translation, and a board of site zones (Clear / N open / Emergency).
- Emergencies: red banner + siren on the dashboard and a Discord `@here`.
- Each hazard has a **Mark resolved** check box; when every hazard in a zone is resolved, the zone turns green.

## How it works
- **Vapi** handles the phone number, speech-to-text (Deepgram nova-3), the voice agent (GPT-4.1 with tool calling) and text-to-speech (Azure neural voices).
- On each inbound call Vapi asks our **FastAPI** backend for an assistant; we look the caller up in the site roster and return one that listens and speaks in that worker's language (English, Chinese, Spanish today).
- The agent calls `report_hazard` / `report_emergency`. The backend stores the report (SQLite), answers instantly, and posts to Discord in the background. The dashboard polls the backend every 1.5 s.

## Scalability
- Works on **any phone** — smartphone, flip phone, or a cellular earpiece / smart hard hat that can dial one number. Nothing to install, no accounts, no training.
- Uses the **phone network**, which already reaches every jobsite. Adding a worker is one line in the roster; adding a language is one entry (transcriber language + voice); adding a zone is one line.
- The backend only reacts to webhooks, so one deployment can serve many sites.

## Innovation
- **The report is the conversation.** No forms: the agent turns free speech into a structured hazard (zone, type, severity, original words, translation) and asks a follow-up only when something is missing.
- **Per-caller language.** The same number speaks Chinese to one worker and English to the next, and the manager always gets English.
- **Hands-free in, accountable out.** Every spoken report becomes an item the manager has to close, so nothing reported by voice gets lost.

## Real-world impact
A hazard seen by one worker reaches the safety manager in seconds, in English, with the worker's exact words, without anyone stopping work to look at a screen. The manager gets a timestamped record of every report and when it was resolved.

## How we used AI coding tools
- **Tool:** Claude Code (Claude Opus 5.5) in the Claude desktop app, for the whole build: backend, Vapi integration, dashboard, simulator, tests, deployment debugging and this write-up.
- **Spec as the acceptance test.** Before the event we wrote a design spec (allowed ideation) whose demo script doubled as the acceptance test, with milestones and a cut order. Claude built milestone by milestone against it and re-planned when constraints changed (one phone, English-only demo, no outbound calls on a trial account).
- **Docs, not memory.** Claude checked every Vapi API field (webhook payloads, tool-call response format, transcriber languages, voices) against the live documentation instead of guessing.
- **Simulator first.** Claude wrote a call simulator and mocked end-to-end checks so the flow was verified before spending real call minutes.
- **Debugging from real logs.** When the first real call hung up, Claude traced it from the Vapi call record and server log to the tunnel (large webhook bodies stalling over QUIC on a phone hotspot) and switched it to HTTP/2; it also fixed misheard words ("plank" → "tank") with Deepgram keyterms and empty captions by switching to `conversation-update`.
- **Design.** Claude used a UI/UX design skill to pick an operations-dashboard design system (dark, high-contrast, safety orange) for the manager screen.
