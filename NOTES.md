# NOTES — choices where the spec left room

- **No outbound calls.** Free Vapi numbers can't call out and a Twilio trial can't buy a number without upgrading, so warnings go to the safety manager (dashboard + Discord) instead of phoning coworkers. The worker side stays voice-only.
- Vapi LLM `openai` / `gpt-4.1` (fast, non-reasoning, reliable tool calls). Transcriber Deepgram `nova-3` in the caller's roster language; English gets `keyterm` prompting (`plank`, `scaffold`, zone names…) because the first real call heard "plank" as "tank". Voices: Azure `andrew` (en), `zh-CN-XiaoxiaoNeural` (zh), `es-MX-DaliaNeural` (es).
- The assistant says "Safe Line" as two words; the TTS read "SafeLine" as "Saphylline".
- Calls end through Vapi's built-in `endCall` tool; `endCallMessage` is the per-language goodbye.
- Live transcript comes from `conversation-update` (whole conversation after every turn, stored idempotently per call, fragments merged to one line per turn). Subscribing to `transcript[transcriptType="final"]` delivered nothing in a real call.
- **Resolve**: `hazards.resolved_at` (added by an in-place migration). Open hazards sort first; a zone shows CLEAR when it has no open hazard and EMERGENCY when an open one is an emergency.
- The webhook URL given to Vapi comes from the Host header Vapi used to reach us (the tunnel); `PUBLIC_BASE_URL` is only for localhost requests (the simulator).
- Callers are matched to the roster on the last 10 digits; placeholder numbers never match.
- Repeated `toolCallId`s are ignored (no double logging). Unknown zone in `report_hazard`: nothing stored, the model is told to ask which zone.
- Emergencies are stored with `hazard_type = "EMERGENCY"`, `severity = high`; zone may be `unknown`.
- Tunnel: cloudflared with `--protocol http2`. Over QUIC on a phone hotspot, Vapi's ~20 KB `assistant-request` body stalled and Vapi hung up (`assistant-request-returned-error`). The venue Wi-Fi blocked new quick tunnels, so the laptop runs on a phone hotspot.
- Dashboard design: dark OLED, industrial slate + safety orange (ui-ux-pro-max "Real-Time / Operations"), SVG icons, ≥44 px resolve targets, focus rings, reduced-motion respected.
