# SafeLine — brief for the video-making agent

You are making the **demo video** for a hackathon submission (c0mpiled-16 @ UCSD, track **"No App"**: *the user experience must not require looking at a screen*). Judges only see the submitted materials and score **scalability, innovation and real-world impact**. The first 10 seconds decide whether they keep watching.

## Deliverable

- MP4, H.264 + AAC, **1920×1080, 30 fps, at most 90 seconds** (aim for 80–88 s).
- Upload to YouTube as **Unlisted or Public** (the submission form requires a publicly viewable link) and return the link.
- English narration and English on-screen text. Captions for every spoken line, including the phone call (many judges watch muted).

## What SafeLine is (say this accurately)

- **SafeLine is a device, not a hotline.** The final product is a **small voice device each worker wears all day, like the walkie-talkie they already carry**. Press once and talk, in their own language — but instead of a noisy shared channel, they talk to an AI that logs the hazard, alerts the safety manager and answers questions. No app, no screen, hands stay on the job.
- **What exists today: the software behind the device.** An AI voice agent, a backend, and the safety manager's web dashboard. **In the prototype, a phone call stands in for the device**; the backend is the same either way.
- A worker can **report a hazard**, **report an emergency**, and **ask whether a zone is safe** (the agent reads open hazards back from the live database).
- The **safety manager** sees each report within seconds on the dashboard (live call captions, hazard feed with the worker's own words, a zone board: Clear / Open / Emergency) and ticks hazards off when they are fixed.

Never call it a "safety line" or "hotline". Do not claim the hardware exists: device imagery (a compact walkie-talkie-style unit or a clip-on earpiece) is welcome but must carry an on-screen **"Concept"** label.

## Inputs from the founder

Two screen recordings of the real dashboard (1920×1080):

| Recording | Content |
|---|---|
| **Before the call** | The dashboard with no hazard yet (Zone B shows **CLEAR**). |
| **After the call** | The same dashboard after the report: the call's captions in the left panel, the hazard card *"loose scaffold plank — Zone B — HIGH"* in the middle, **Zone B → 1 OPEN** on the right. It may also show the manager clicking **Mark resolved** and Zone B turning **CLEAR** again. |

Use the "before" recording while the phone call plays, then cut or cross-fade to the "after" recording at the moment the call ends, so the dashboard visibly updates.

## The phone-call overlay (you build this)

Composite an animated **phone call screen in the bottom-right corner** over the dashboard recordings.

- **Size and position:** about 300 × 600 px at 1080p, 40 px from the right edge and 30 px from the bottom. The zone cards sit in the top half of the right column; keep the phone below them so Zone A/B/C stay visible.
- **Look:** a clean, realistic call screen (rounded phone frame, soft shadow). Caller name **"Safe Line"**, number **+1 (858) 348-9303**.
- **States, in order:**
  1. **Calling…** (about 1.5 s, ringback tone).
  2. **Connected** with a running timer (00:01, 00:02, …), a small "speaking" waveform, and a caption bubble showing the current line labelled **Safe Line** or **Worker**.
  3. **Call ended** (the agent hangs up by itself) for about 1 s, then the phone fades out.
- Put a small tag above the phone: **"Prototype: a phone call stands in for the device"**.
- Recommended (honest, and judges respect it): a tiny **"Reenacted call"** label on the phone, since the call audio is re-voiced.

### Call audio

- Two voices: **Safe Line** = calm male US English voice (the live system uses Azure neural voice "Andrew"; match it if you can). **Worker** = a different voice, slightly noisier.
- Apply a telephone EQ (band-pass about 300–3400 Hz) to both call voices so they sound like a phone call. Keep the narration voice clean.
- Use exactly the lines below; they match what the live system says.

**Call 1: report (plays over the "before" recording, then cut to "after")**

> **Safe Line:** Safe Line. Report a hazard, or ask me about a zone.
> **Worker:** There's a loose plank on the level 3 scaffold in Zone B. Somebody could fall.
> **Safe Line:** Got it. The safety manager has been alerted. Stay safe. Goodbye.
> *(call ends by itself → cut to the "after" recording: hazard appears, Zone B turns orange)*

**Call 2: question (plays over the "after" recording; crop or zoom toward the hazard feed and zone board)**

> **Safe Line:** Safe Line. Report a hazard, or ask me about a zone.
> **Worker:** Is Zone B safe right now?
> **Safe Line:** Zone B has one open hazard: a loose scaffold plank. Avoid that area until it's fixed.
> **Worker:** Okay, thanks.
> **Safe Line:** Stay safe. Goodbye.

If the "after" recording includes the manager clicking **Mark resolved**, show it after Call 2 (Zone B turns green). Optional extra beat if time allows: a short Call 3 with *"Is Zone B safe now?" → "Zone B is clear. No open hazards."*

## Script and timing (targets)

| Time | Visual | Narration / on-screen text |
|---|---|---|
| 0:00–0:07 | Construction-site b-roll (stock is fine) or `story.png` | "My family has a background in construction. Most crews we know still talk over walkie-talkies." |
| 0:07–0:20 | Walkie-talkie close-ups or `pain.png` | "But a radio is still an interface. You need a free hand to push to talk. Everyone shares one noisy channel, so if you weren't listening, you missed it. Nothing is recorded. And crews speak different languages." |
| 0:20–0:29 | **Concept** visual of a worker wearing a small walkie-talkie-style device, hands busy (label "Concept"), then `product.png` | "Safe Line is a voice safety device. It works like the radio you already carry — press once and talk — but instead of a noisy channel, you're talking to an A.I. that listens." |
| 0:29–0:33 | Text card: "Today's prototype is the software. A phone call stands in for the device." | (read the card) |
| 0:33–0:50 | **Call 1** over the "before" recording → cut to "after" | No narration during the call. After the cut, one line: "The safety manager sees it in seconds, in the worker's own words." |
| 0:50–1:06 | **Call 2** (question) over the "after" recording | Lower-third: "Workers ask by voice. Answers come from live site data." |
| 1:06–1:15 | Manager clicks **Mark resolved** → Zone B green (if recorded; otherwise `dash_resolved.png`) | "When it's fixed, the manager checks it off. Nothing reported by voice gets lost." |
| 1:15–1:24 | End card `close.png` | "Workers talk. Managers see. Nothing gets lost. Safe Line." |

Editing notes: cut dead air, keep the call snappy (no long pauses between lines), duck any music under call audio and narration, and zoom gently toward the dashboard panel that changes (left = live call captions, middle = hazard feed, right = zone board).

## Other assets (in the SafeLine project folder)

| File | What it is |
|---|---|
| `video/build/story.png`, `pain.png`, `product.png`, `close.png` | Title cards (1920×1080) in the brand style. |
| `video/build/dash_call.png`, `dash_hazard.png`, `dash_resolved.png`, `dash_emergency.png` | Dashboard stills, for backup or b-roll. |
| `video/SafeLine_draft.mp4` | A rough 81 s draft (robotic voice) that shows the intended pacing. Do not submit it. |

## Brand

- Light and minimal. Background `#f7f7f8`, surfaces `#ffffff`, text `#18181b`, secondary text `#6b6b76`, dividers `#e4e4e7`.
- Color only for status: emergency red `#dc2626`, open amber `#c2410c`, resolved green `#15803d`.
- Font: **Inter** (600 for headings, 400 for body). Logo: black rounded square with a white shield-check icon, wordmark "SafeLine".
- Narration: calm and confident, no hype; a natural human voice is far better than robotic text-to-speech. Say the name as "Safe Line" (two words).

## Checklist before upload

- [ ] ≤ 90 s, 1920×1080, even audio levels, captions on every spoken line
- [ ] The phone overlay never covers the zone cards, and the dashboard visibly updates when Call 1 ends
- [ ] "Concept" label on any device imagery, and the prototype tag on the phone
- [ ] SafeLine is presented as a device (never a "safety line" or "hotline")
- [ ] No personal phone numbers visible (the Safe Line number is fine)
- [ ] The link plays in a private/incognito window
