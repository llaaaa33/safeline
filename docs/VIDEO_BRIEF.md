# SafeLine — brief for the video-making agent

You are making the **demo video** for a hackathon submission (c0mpiled-16 @ UCSD, track **"No App"**: *the user experience must not require looking at a screen*). Judges only see the submitted materials, and judge **scalability, innovation and real-world impact**. The first 10 seconds decide whether they keep watching.

## Deliverable

- MP4, H.264 + AAC, **1920×1080, 30 fps, at most 90 seconds** (aim for 80–88 s).
- Upload to YouTube as **Unlisted or Public** (the form requires a publicly viewable link) and return the link.
- English narration and English on-screen text. Burned-in captions for every spoken line (many judges watch muted).

## What SafeLine is (say this accurately)

- **Product vision:** an **earpiece every construction worker wears all day**. To report a hazard or ask a question they press one button (or say "Safe Line") and just talk, in their own language. No app, no screen, hands stay on the job.
- **What exists today: the software.** An AI voice agent on a phone number, a backend, and a safety manager's dashboard. **In the prototype, a phone call stands in for the earpiece**; the backend is exactly the same either way.
- Workers can **report a hazard**, **report an emergency**, and **ask whether a zone is safe** (the agent reads back open hazards from the live database).
- The **safety manager** sees each report in seconds on the dashboard (live call captions, hazard feed with the worker's own words, zone board) and checks hazards off when fixed. Emergencies raise an alarm.

**Do not** claim the earpiece hardware exists. Concept imagery of a worker wearing an earpiece is welcome, but label it **"Concept"** on screen. **Do not** fake or re-voice the phone calls: the demo section must use the real call audio and real screen recording provided below.

## Story and script (narration — keep the wording, timings are targets)

| Time | Visual | Narration / on-screen text |
|---|---|---|
| 0:00–0:07 | Construction site b-roll (stock is fine) or the "story" card | "My family has a background in construction. Most crews we know still talk over walkie-talkies." |
| 0:07–0:20 | Walkie-talkie close-ups / the "pain" card (4 points) | "But a radio is still an interface. You need a free hand to push to talk. Everyone shares one noisy channel — if you weren't listening, you missed it. Nothing is recorded. And crews speak different languages." |
| 0:20–0:30 | **Concept** visual: worker wearing an earpiece, hands busy. Label "Concept". Then the "product" card | "Safe Line is a safety line with no interface: an earpiece every worker wears. Press once, and just talk." |
| 0:30–0:34 | Text card: "Today's prototype: the software. A phone call stands in for the earpiece." | (read the card) |
| 0:34–0:58 | **Real call 1 — report** (from `demo_real.mp4`, see timecodes). Show the dashboard as the hazard appears and Zone B turns orange. Real call audio, captions. | Mostly let the real call play. One short line over the dashboard: "The safety manager sees it in seconds, in the worker's own words." |
| 0:58–1:12 | **Real call 2 — question** ("Is Zone B safe right now?") with the agent's answer. | Let the real call play. Lower-third: "Workers ask by voice. Answers come from live site data." |
| 1:12–1:20 | Manager clicks **Mark resolved** → Zone B turns green (and, if recorded, real call 3 answering "Zone B is clear"). | "When it's fixed, the manager checks it off. Nothing reported by voice gets lost." |
| 1:20–1:28 | End card: logo + "Workers talk. Managers see. Nothing gets lost." + "SafeLine · c0mpiled-16 · No App track" | "Workers talk. Managers see. Nothing gets lost. Safe Line." |

Editing notes for the real calls: cut dead air and ring time, keep both sides' key lines, zoom/crop into the dashboard panel that changes (left = live call captions, middle = hazard feed, right = zone board). Duck any music under the call audio.

## Assets (all in the SafeLine repo folder on this computer)

| File | What it is |
|---|---|
| `video/assets/demo_real.mp4` | **Screen recording of the dashboard during the real calls, with the real call audio already placed at the right time.** |
| `video/assets/timecodes.json` | Start/end second of each call inside `demo_real.mp4`, plus a one-line summary per call. |
| `video/assets/call_N.wav`, `call_N_transcript.txt` | Each real call on its own (both sides, as recorded by the phone platform) and its transcript — use for captions. |
| `video/build/story.png`, `pain.png`, `product.png`, `close.png` | Title cards (1920×1080) in the brand style. |
| `video/build/dash_*.png` | Dashboard stills (call, hazard, resolved, emergency) from simulated data — use only as backup/b-roll, not as the "real call" segment. |
| `video/SafeLine_draft.mp4` | A rough 81 s draft (robotic TTS, simulated data) showing the intended pacing. Do not submit it. |

## Brand

- Light and minimal. Background `#f7f7f8`, surfaces `#ffffff`, text `#18181b`, secondary text `#6b6b76`, dividers `#e4e4e7`.
- Color only for status: emergency red `#dc2626`, open/amber `#c2410c`, resolved green `#15803d`.
- Font: **Inter** (600 for headings, 400 for body). Logo: black rounded square with a white shield-check icon, wordmark "SafeLine".
- Voice: calm, confident, no hype. A natural human voice is much better than robotic TTS; the founder may record the narration.
- Pronounce the name "Safe Line" (two words).

## Checklist before upload

- [ ] ≤ 90 s, 1920×1080, audio levels even, captions on every spoken line
- [ ] The demo section uses the real recording and real call audio
- [ ] "Concept" label on any earpiece imagery; the prototype card is present
- [ ] No phone numbers or personal data visible
- [ ] Link works in a private/incognito window
