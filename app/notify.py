"""Discord webhook for manager alerts. `python -m app.notify` posts a test message."""
import asyncio
import logging
import os

import httpx

log = logging.getLogger("safeline.notify")

SEVERITY_ICON = {"high": "🔴", "medium": "🟠", "low": "🟡"}
LANGUAGE_TAG = {"en": "EN", "zh": "中文", "es": "ES"}


async def send_discord(content: str, urgent: bool = False) -> bool:
    url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        log.warning("DISCORD_WEBHOOK_URL not set; skipping Discord message")
        return False
    # Webhooks only ping @here when allowed_mentions permits it.
    payload = {"content": content[:1990], "allowed_mentions": {"parse": ["everyone"] if urgent else []}}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json=payload)
    except httpx.HTTPError as e:
        log.error("Discord webhook error: %s", e)
        return False
    if r.status_code >= 300:
        log.error("Discord webhook failed: %s %s", r.status_code, r.text[:300])
        return False
    return True


def format_hazard(hazard: dict, zone_name: str, recipients: list[str]) -> str:
    sev = (hazard["severity"] or "medium").lower()
    lang = hazard["language"] or "en"
    calling = ", ".join(recipients) if recipients else "nobody else is in this zone"
    return (
        f"{SEVERITY_ICON.get(sev, '⚠️')} **{sev.upper()} hazard** — {zone_name}\n"
        f"**Hazard:** {hazard['hazard_type']}\n"
        f"**Original ({LANGUAGE_TAG.get(lang, lang)}):** {hazard['description_original']}\n"
        f"**English:** {hazard['description_en']}\n"
        f"**Reported by:** {hazard['caller_name']} · {hazard['created_at'][11:19]}\n"
        f"**Calling now:** {calling}"
    )


def format_emergency(hazard: dict, zone_name: str, supervisor: str) -> str:
    lang = hazard["language"] or "en"
    return (
        f"🚨 URGENT @here — **EMERGENCY in {zone_name}**\n"
        f"**What happened:** {hazard['description_en']}\n"
        f"**Original ({LANGUAGE_TAG.get(lang, lang)}):** {hazard['description_original']}\n"
        f"**Reported by:** {hazard['caller_name']} · {hazard['created_at'][11:19]}"
        + (f"\n**Calling supervisor:** {supervisor}" if supervisor else "")
    )


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    ok = asyncio.run(send_discord("✅ SafeLine test message: the Discord webhook works."))
    print("sent" if ok else "FAILED (check DISCORD_WEBHOOK_URL in .env)")
