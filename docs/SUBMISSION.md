# SafeLine — submission draft

**Track:** No App
**Video:** _(link)_ · **Code:** https://github.com/llaaaa33/safeline

## Form: 2 Sentence Description of the Project

SafeLine is a hands-free voice safety device for construction workers: it works like the walkie-talkie they already carry, but instead of a noisy shared channel they talk to an AI that understands their language, so there is no app and no screen. Every report reaches the safety manager's live dashboard in seconds, emergencies raise an alarm, and workers can ask by voice whether a zone is safe — today's prototype is the software, with a phone call standing in for the device.

## One line
A walkie-talkie that listens: workers report hazards by voice, and the safety manager sees and closes them on one live screen.

## The problem
On a construction site the people who first see a hazard — a loose plank, an open edge, a leaking line — are wearing gloves, standing on ladders, working in noise, and often speak different languages. Most crews still coordinate over walkie-talkies: you need a free hand to push to talk, everyone shares one noisy channel (if you weren't listening, you missed it), nothing is recorded, and there is no help across languages. Hazards get shouted, forgotten, or never reported.

## The product
- **The device (vision):** a small voice device each worker wears all day, like the radio they already carry. Press once and talk, in any language. No app, no screen, hands stay on the job.
- **Today's prototype:** the software behind it. A phone call stands in for the device; the AI agent, backend and dashboard are the same either way.

## What the worker experiences (no interface)
1. **Report by voice.** Press and talk: "There's a loose plank on the level 3 scaffold in Zone B." SafeLine asks one follow-up only if the zone or hazard is unclear, then confirms the safety manager has been alerted.
2. **Ask by voice.** "Is Zone B safe right now?" SafeLine reads back the open hazards from live site data, or says the zone is clear.
3. **Emergency by voice.** "Help, someone fell off a ladder!" SafeLine immediately says help is on the way and raises an urgent alert.

## What the safety manager sees
- A live dashboard: the conversation as it happens (captions), the hazard feed with the worker's own words and an English translation, and a board of site zones (Clear / N open / Emergency).
- Emergencies: red banner + siren on the dashboard and a Discord `@here`.
- Each hazard has a **Mark resolved** check box; when every hazard in a zone is resolved, the zone turns green, and workers who ask are told it's clear.

## How it works
- **Vapi** handles the voice connection, speech-to-text (Deepgram nova-3), the voice agent (GPT-4.1 with tool calling) and text-to-speech (Azure neural voices).
- For each conversation the **FastAPI** backend looks the worker up in the site roster and returns an agent that listens and speaks in that worker's language (English, Chinese, Spanish today).
- The agent calls `report_hazard`, `report_emergency` or `check_zone`. The backend stores reports (SQLite), answers instantly, posts to Discord in the background, and the dashboard polls it every 1.5 s.

## Scalability
- The device only needs a voice connection to one number, so the same backend already works from any phone today — no install, no accounts, no training.
- Adding a worker is one line in the roster; adding a language is one entry (transcriber language + voice); adding a zone is one line.
- The backend only reacts to webhooks, so one deployment can serve many sites.

## Innovation
- **The report is the conversation.** No forms: the agent turns free speech into a structured hazard (zone, type, severity, original words, translation) and asks a follow-up only when something is missing.
- **Two-way voice.** Workers don't just report; they can ask about a zone and hear live, data-backed answers.
- **Per-worker language.** Each worker speaks their own language; the manager always gets English.
- **Hands-free in, accountable out.** Every spoken report becomes an item the manager has to close.

## Real-world impact
A hazard seen by one worker reaches the safety manager in seconds, in English, with the worker's exact words, and every other worker can check a zone by asking — without anyone stopping work to look at a screen. The manager gets a timestamped record of every report and when it was resolved.

## How we used AI coding tools
- **Tool:** Claude Code (Claude Opus 5.5) in the Claude desktop app, for the whole build: backend, Vapi integration, dashboard, simulator, tests, deployment debugging and this write-up.
- **Spec as the acceptance test.** Before the event we wrote a design spec (allowed ideation) whose demo script doubled as the acceptance test, with milestones and a cut order. Claude built milestone by milestone against it and re-planned when constraints changed (one phone, English-only demo, no outbound calls on a trial account).
- **Docs, not memory.** Claude checked every Vapi API field (webhook payloads, tool-call response format, transcriber languages, voices) against the live documentation instead of guessing.
- **Simulator first.** Claude wrote a call simulator and mocked end-to-end checks so the flow was verified before spending real call minutes.
- **Debugging from real logs.** When the first real call hung up, Claude traced it from the Vapi call record and server log to the tunnel (large webhook bodies stalling over QUIC on a phone hotspot) and switched it to HTTP/2; it also fixed misheard words ("plank" → "tank") with Deepgram keyterms and empty captions by switching to `conversation-update`.
- **Design.** Claude used a UI/UX design skill (accessibility, touch targets, semantic status colors) to design a light, minimal manager screen.
