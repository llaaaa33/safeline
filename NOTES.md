# NOTES — choices where the spec left room

- Vapi LLM `openai` / `gpt-4.1` (fast, non-reasoning, reliable tool calls). Transcriber Deepgram `nova-3` in the caller's roster language. Voices: Azure `andrew` (en), `zh-CN-XiaoxiaoNeural` (zh), `es-MX-DaliaNeural` (es).
- Calls end through Vapi's built-in `endCall` tool; `endCallMessage` is the per-language goodbye.
- "Delivered" = the outbound call reached `status-update: in-progress` (answered; voicemail counts too). Ending without reaching it = `failed`.
- English alerts use a fixed template with no LLM, so the closed loop never depends on an LLM. zh/es are LLM-translated (Anthropic `claude-opus-5-5` if `ANTHROPIC_API_KEY`, else OpenAI `gpt-4.1-mini`); any error falls back to English.
- The webhook URL given to Vapi comes from the Host header Vapi used to reach us (the tunnel); `PUBLIC_BASE_URL` is used only for localhost requests (the simulator).
- Callers are matched to the roster on the last 10 digits of the phone number.
- Repeated `toolCallId`s are ignored (no double logging or double calls).
- Unknown zone in `report_hazard`: nothing stored; the tool result tells the model to ask which zone.
- Emergencies: Discord `🚨 URGENT @here` + red dashboard banner with an alarm (manager sees it on screen). The supervisor phone call only happens when `SUPERVISOR_PHONE` is set.
- `seed.local.json` (gitignored) overrides `seed.json` so real phone numbers stay out of git.
- Added `scripts/configure_vapi_number.py` (sets the number's Server URL, detaches any fixed assistant) and `python -m app.notify` (Discord test).
- Free Vapi numbers can't place outbound calls; the demo uses a Twilio number imported into Vapi.
