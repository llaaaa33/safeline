# SafeLine — submission draft

**Track:** No App
**Video:** _(link)_ · **Code:** _(link)_

## One line
SafeLine is a safety network for construction sites that workers use without ever touching a screen: they report a hazard by talking, and every coworker in that zone is warned by a phone call that speaks to them in their own language.

## The problem
On a construction site the people who first see a hazard — a loose plank, an open edge, a leaking line — are wearing gloves, standing on ladders, working in noise, and often speak different languages. Safety apps assume someone will stop, take out a phone, unlock it, and type. In practice the warning travels by shouting, or not at all, and the coworker one floor up never hears it.

## What the worker experiences (no interface)
1. **Report by voice.** "Hey Siri, call SafeLine." The worker describes the hazard in their own words and language. SafeLine asks one follow-up only if the zone or hazard is unclear, logs it, and tells them how many coworkers it is warning. Hands stay on the job.
2. **Get warned by voice.** Every other worker in that zone receives a call within seconds. With auto-answer on, the warning plays straight into their earpiece — no tap, no screen: *"Safety alert for Zone B, level 3 scaffold: loose scaffold plank. Avoid the area until it is cleared."* They can ask a quick question about it.
3. **Emergency by voice.** "Help, someone fell off a ladder!" SafeLine immediately says help is on the way and raises an urgent alert to the safety manager.

The only screen in the system belongs to the safety manager: a live dashboard (transcript, hazard feed, who has been reached) and Discord alerts with `@here` for emergencies.

## How it works
- **Vapi** handles the phone number, speech-to-text (Deepgram nova-3), the voice agent (GPT-4.1 with tool calling) and text-to-speech (Azure neural voices).
- On each inbound call Vapi asks our **FastAPI** backend for an assistant; we look the caller up in the site roster and return one that listens and speaks in that worker's language (English, Chinese, Spanish today).
- The agent calls `report_hazard` / `report_emergency`. The backend stores the report (SQLite), answers instantly, and in the background posts to Discord and **places outbound calls** to every other worker in the zone, translated per recipient.
- Call status webhooks close the loop: the dashboard shows each warning as calling → delivered (answered) or failed.

## Scalability
- Works on **any phone** — smartphone, flip phone, or a cellular earpiece / smart hard hat that can dial one number. Nothing to install, no accounts, no training.
- Uses the **phone network**, which already reaches every jobsite. Adding a worker is one line in the roster; adding a language is one entry (transcriber language + voice).
- The backend is stateless per call and only reacts to webhooks, so one deployment can serve many sites.

## Innovation
- **Voice in, voice out, closed loop.** Not just a hotline that logs reports: a spoken report turns into spoken warnings for exactly the people at risk, and the system knows who was actually reached.
- **Per-caller language.** The same number speaks Chinese to one worker and English to the next, and translates the warning for each recipient.

## Real-world impact
A hazard seen by one worker reaches everyone in that zone in seconds, in a language they understand, without anyone stopping work to look at a screen. The manager gets a live, timestamped record of every report and every warning.

## How we used AI coding tools
- **Tool:** Claude Code (Claude Opus 5.5) in the Claude desktop app, for the whole build: backend, Vapi integration, dashboard, simulator, tests and this write-up.
- **Spec as the acceptance test.** Before the event we wrote a design spec (allowed ideation) whose demo script doubled as the acceptance test and whose milestones had a fixed cut order. Claude built milestone by milestone against it.
- **Docs, not memory.** Claude checked every Vapi API field (webhook payloads, tool-call response format, transcriber languages, voices, outbound-call API) against the live documentation instead of guessing, and kept a list of the gotchas (e.g. free Vapi numbers can't place outbound calls; tool results must be strings with HTTP 200).
- **Simulator first.** Claude wrote a call simulator and mocked end-to-end checks (Vapi and Discord replaced by fakes) so the whole flow — logging, translation fallback, outbound calls, delivered/failed status, emergencies — was verified before spending real call minutes.
- **Design partner.** Claude helped re-plan the demo around our constraints (one phone → the laptop acts as the second line; English-only demo) and around the No App theme.
