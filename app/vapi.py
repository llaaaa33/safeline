"""Vapi assistant configs (inbound reporter, outbound alert caller) and the outbound call helper.

Field names checked against docs.vapi.ai: assistant-request response {"assistant": {...}},
function tools with "server": {"url"}, built-in {"type": "endCall"}, deepgram nova-3 (en/es/zh),
azure voices, POST /call with phoneNumberId + customer.number + transient assistant.
"""
import logging
import os

import httpx

log = logging.getLogger("safeline.vapi")

VAPI_API = "https://api.vapi.ai"
LLM = {"provider": "openai", "model": "gpt-4.1", "temperature": 0.2}

LANGUAGES = {
    "en": {"name": "English", "voice": {"provider": "azure", "voiceId": "andrew"},
           "first_message": "SafeLine. What's the hazard, and where?", "goodbye": "Stay safe. Goodbye."},
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

After the tool returns, confirm in one sentence, including how many coworkers are being warned, then end the call.
Never ask the caller to look at a screen or open an app."""

ALERT_PROMPT = """You are SafeLine, calling a construction worker with a safety alert.
Speak only {language_name}. Keep every turn under 15 words.
You have already said: "{message}"
Facts: zone = {zone_name}; hazard = {hazard_type}; report = {description_en}.
Answer brief questions about this one hazard only. For anything else, say you can only talk about this alert.
When the worker acknowledges, says thanks, or has no questions, call endCall.
Never ask the worker to look at a screen or open an app."""


def lang_cfg(language: str) -> dict:
    return LANGUAGES.get(language, LANGUAGES["en"])


def _transcriber(language: str) -> dict:
    return {"provider": "deepgram", "model": "nova-3", "language": language if language in LANGUAGES else "en"}


def _report_tools(zone_ids: list[str], webhook_url: str) -> list[dict]:
    server = {"url": webhook_url}
    text = {"type": "string"}
    return [
        {
            "type": "function",
            "server": server,
            "function": {
                "name": "report_hazard",
                "description": "Log a construction-site hazard and phone the coworkers in that zone.",
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
        "serverMessages": ["tool-calls", 'transcript[transcriptType="final"]', "status-update", "end-of-call-report"],
    }


def build_alert_assistant(*, message: str, language: str, zone_name: str, hazard_type: str,
                          description_en: str, webhook_url: str) -> dict:
    cfg = lang_cfg(language)
    prompt = ALERT_PROMPT.format(language_name=cfg["name"], message=message, zone_name=zone_name,
                                 hazard_type=hazard_type, description_en=description_en)
    return {
        "name": "SafeLine Alert",
        "firstMessage": message,
        "transcriber": _transcriber(language),
        "voice": cfg["voice"],
        "model": {**LLM, "messages": [{"role": "system", "content": prompt}], "tools": [{"type": "endCall"}]},
        "endCallMessage": cfg["goodbye"],
        "maxDurationSeconds": 60,
        "server": {"url": webhook_url},
        "serverMessages": ["status-update", "end-of-call-report"],
    }


async def create_outbound_call(phone: str, assistant: dict) -> tuple[str | None, str | None]:
    """Place a call. Returns (vapi_call_id, None) or (None, error)."""
    key = os.getenv("VAPI_API_KEY", "").strip()
    number_id = os.getenv("VAPI_PHONE_NUMBER_ID", "").strip()
    if not key or not number_id:
        return None, "VAPI_API_KEY / VAPI_PHONE_NUMBER_ID not set"
    if not phone or "X" in phone:
        return None, f"invalid phone number {phone!r}"
    body = {"phoneNumberId": number_id, "customer": {"number": phone}, "assistant": assistant}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(f"{VAPI_API}/call", json=body, headers={"Authorization": f"Bearer {key}"})
    except httpx.HTTPError as e:
        return None, f"Vapi request failed: {e}"
    if r.status_code >= 300:
        return None, f"Vapi {r.status_code}: {r.text[:300]}"
    return r.json().get("id"), None
