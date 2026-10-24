"""Turn a hazard into a short spoken alert in the recipient's language.

English uses a fixed template (no LLM) so the closed loop never depends on an LLM.
zh / es use Anthropic (if ANTHROPIC_API_KEY) or OpenAI (if OPENAI_API_KEY); any failure
falls back to the English template.
"""
import logging
import os

import httpx

log = logging.getLogger("safeline.llm")

LANGUAGE_NAMES = {"en": "English", "zh": "Mandarin Chinese (Simplified)", "es": "Spanish"}
DEFAULT_ANTHROPIC_MODEL = "claude-opus-5-5"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
TIMEOUT_S = 15


def english_alert(zone_name: str, hazard_type: str) -> str:
    return f"Safety alert for {zone_name}: {hazard_type}. Avoid the area until it is cleared."


def _prompt(zone_name: str, hazard_type: str, description_en: str, language: str) -> tuple[str, str]:
    system = (
        "You write short spoken safety alerts for construction workers. "
        f"Reply with only the alert text in {LANGUAGE_NAMES.get(language, 'English')}: "
        "at most 2 short sentences, no markdown, no quotes. Use this form, translated naturally: "
        "'Safety alert for {zone name}: {hazard}. Avoid the area until it is cleared.'"
    )
    user = f"Zone name: {zone_name}\nHazard: {hazard_type}\nWorker's report (English): {description_en}"
    return system, user


async def _anthropic(system: str, user: str) -> str | None:
    import anthropic

    client = anthropic.AsyncAnthropic(timeout=TIMEOUT_S, max_retries=1)
    try:
        response = await client.beta.messages.create(
            model=os.getenv("ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL,
            max_tokens=4000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": "low"},
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except anthropic.RateLimitError:
        log.error("Anthropic rate limited")
        return None
    except anthropic.APIStatusError as e:
        log.error("Anthropic API error %s: %s", e.status_code, e.message)
        return None
    except anthropic.APIConnectionError as e:
        log.error("Anthropic connection error: %s", e)
        return None
    if response.stop_reason == "refusal":
        log.error("Anthropic refused the translation")
        return None
    return "".join(b.text for b in response.content if b.type == "text").strip() or None


async def _openai(system: str, user: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                json={"model": os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL,
                      "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
            )
        if r.status_code >= 300:
            log.error("OpenAI error %s: %s", r.status_code, r.text[:300])
            return None
        return r.json()["choices"][0]["message"]["content"].strip() or None
    except (httpx.HTTPError, KeyError, ValueError) as e:
        log.error("OpenAI translation failed: %s", e)
        return None


async def translate_alert(zone_name: str, hazard_type: str, description_en: str, language: str) -> str:
    """Spoken alert for one recipient. Never raises."""
    fallback = english_alert(zone_name, hazard_type)
    if language == "en":
        return fallback
    system, user = _prompt(zone_name, hazard_type, description_en, language)
    text = None
    if os.getenv("ANTHROPIC_API_KEY"):
        text = await _anthropic(system, user)
    elif os.getenv("OPENAI_API_KEY"):
        text = await _openai(system, user)
    else:
        log.warning("No LLM key set; sending the English alert to a %s speaker", language)
    return text or fallback
