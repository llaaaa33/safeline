"""Per-caller Vapi assistant config for inbound hazard reports.

Field names checked against docs.vapi.ai: assistant-request response {"assistant": {...}},
function tools with "server": {"url"}, built-in {"type": "endCall"}, deepgram nova-3 (en/es/zh),
azure voices.
"""
LLM ={"provider": "openai", "model": "gpt-4.1", "temperature": 0.2}

LANGUAGES = {
    "en": {"name": "English", "voice": {"provider": "azure", "voiceId": "andrew"},
           # "Safe Line" as two words: the TTS voice reads "SafeLine" as "Saphylline"
           "first_message": "Safe Line. What's the hazard, and where?", "goodbye": "Stay safe. Goodbye."},
    "zh": {"name": "Mandarin Chinese (Simplified)", "voice": {"provider": "azure", "voiceId": "zh-CN-XiaoxiaoNeural"},
           "first_message": "这里是 SafeLine，请说哪里有什么隐患。", "goodbye": "注意安全，再见。"},
    "es": {"name": "Spanish", "voice": {"provider": "azure", "voiceId": "es-MX-DaliaNeural"},
           "first_message": "SafeLine. ¿Cuál es el peligro y dónde está?", "goodbye": "Cuídese. Adiós."},
}

INBOUND_PROMPT = """You are SafeLine, a hands-free safety line for construction workers.
The caller is {name}. Speak only {language_name}.
Keep every turn under 15 words: the caller is working and the site is noisy.

Goal: capture a hazard report: which zone, what hazard, how severe.
Known zones: {zones}.
If the location does not clearly match a zone, ask once which zone it is.

As soon as you know the zone and the hazard, call report_hazard.
Severity: high = could injure someone right now; medium = needs fixing today; low = minor.
Always fill description_original with the caller's own words and description_en with an English translation.

If the caller mentions an injury, a fall, fire, or says emergency / help, immediately call report_emergency,
then say help is on the way and tell them to stay where they are if it is safe.

After the tool returns, confirm in one sentence that the safety manager has been alerted, then end the call.
Never ask the caller to look at a screen or open an app.
When you say the product name out loud, write it as "Safe Line" (two words)."""


def lang_cfg(language: str) -> dict:
    return LANGUAGES.get(language, LANGUAGES["en"])


# Deepgram keyterm prompting: jobsite words it otherwise mishears ("plank" -> "tank").
KEYTERMS = ["SafeLine", "scaffold", "plank", "ladder", "harness", "Zone A", "Zone B", "Zone C", "loading dock"]


def _transcriber(language: str) -> dict:
    language = language if language in LANGUAGES else "en"
    transcriber = {"provider": "deepgram", "model": "nova-3", "language": language}
    if language == "en":
        transcriber["keyterm"] = KEYTERMS
    return transcriber


def _report_tools(zone_ids: list[str], webhook_url: str) -> list[dict]:
    server = {"url": webhook_url}
    text = {"type": "string"}
    return [
        {
            "type": "function",
            "server": server,
            "function": {
                "name": "report_hazard",
                "description": "Log a construction-site hazard and alert the safety manager.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zone_id": {"type": "string", "enum": zone_ids},
                        "hazard_type": {**text, "description": "Short English label, e.g. 'loose scaffold plank'."},
                        "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                        "description_original": {**text, "description": "The caller's own words, in their language."},
                        "description_en": {**text, "description": "English translation of the caller's words."},
                    },
                    "required": ["zone_id", "hazard_type", "severity", "description_original", "description_en"],
                },
            },
        },
        {
            "type": "function",
            "server": server,
            "function": {
                "name": "report_emergency",
                "description": "Someone is hurt or in immediate danger (fall, fire, injury, 'help', 'emergency').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zone_id": {"type": "string", "enum": zone_ids + ["unknown"]},
                        "description_original": {**text, "description": "The caller's own words, in their language."},
                        "description_en": {**text, "description": "English translation of the caller's words."},
                    },
                    "required": ["zone_id", "description_original", "description_en"],
                },
            },
        },
        {"type": "endCall"},
    ]


def build_inbound_assistant(worker: dict, zones: list[dict], webhook_url: str) -> dict:
    language = worker.get("language", "en")
    cfg = lang_cfg(language)
    prompt = INBOUND_PROMPT.format(
        name=worker.get("name", "a worker"), language_name=cfg["name"],
        zones="; ".join(f"{z['id']} = {z['name']}" for z in zones),
    )
    return {
        "name": "SafeLine",
        "firstMessage": cfg["first_message"],
        "transcriber": _transcriber(language),
        "voice": cfg["voice"],
        "model": {**LLM, "messages": [{"role": "system", "content": prompt}],
                  "tools": _report_tools([z["id"] for z in zones], webhook_url)},
        "endCallMessage": cfg["goodbye"],
        "maxDurationSeconds": 180,
        "server": {"url": webhook_url},
        # conversation-update carries the whole conversation after every turn (drives the live transcript)
        "serverMessages": ["tool-calls", "conversation-update", "status-update", "end-of-call-report"],
    }
