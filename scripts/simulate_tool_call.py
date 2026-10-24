"""Fake a Vapi call against the local backend (no phone, no Vapi credits).

    python scripts/simulate_tool_call.py              # demo step 1: hazard report, zone B
    python scripts/simulate_tool_call.py emergency    # demo step 5: fall from a ladder, zone A
    python scripts/simulate_tool_call.py assistant    # print the assistant Vapi would get for the presenter
    (hazard-zh / emergency-zh: the same in Chinese)
"""
import argparse
import json
import sys
import uuid
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent

SCENARIOS = {
    "hazard": {
        "lines": [("assistant", "SafeLine. What's the hazard, and where?"),
                  ("user", "There's a loose plank on the level 3 scaffold in Zone B. Somebody could fall.")],
        "tool": "report_hazard",
        "args": {
            "zone_id": "B",
            "hazard_type": "loose scaffold plank",
            "severity": "high",
            "description_original": "There's a loose plank on the level 3 scaffold in Zone B. Somebody could fall.",
            "description_en": "There's a loose plank on the level 3 scaffold in Zone B. Somebody could fall.",
        },
        "after": ("assistant", "Got it. Warning one coworker in Zone B now."),
    },
    "emergency": {
        "lines": [("assistant", "SafeLine. What's the hazard, and where?"),
                  ("user", "Help! Someone just fell off a ladder in Zone A!")],
        "tool": "report_emergency",
        "args": {
            "zone_id": "A",
            "description_original": "Help! Someone just fell off a ladder in Zone A!",
            "description_en": "Help! Someone just fell off a ladder in Zone A!",
        },
        "after": ("assistant", "Help is on the way. Stay where you are if it is safe."),
    },
    "hazard-zh": {
        "lines": [("assistant", "这里是 SafeLine，请说哪里有什么隐患。"), ("user", "B区三楼脚手架有一块木板松了，很危险。")],
        "tool": "report_hazard",
        "args": {
            "zone_id": "B",
            "hazard_type": "loose scaffold plank",
            "severity": "high",
            "description_original": "B区三楼脚手架有一块木板松了，很危险。",
            "description_en": "A plank on the level 3 scaffold in Zone B is loose. It is very dangerous.",
        },
        "after": ("assistant", "收到，已记录。正在通知B区的同事。"),
    },
    "emergency-zh": {
        "lines": [("assistant", "这里是 SafeLine，请说哪里有什么隐患。"), ("user", "救命，A区有人从梯子上摔下来了")],
        "tool": "report_emergency",
        "args": {
            "zone_id": "A",
            "description_original": "救命，A区有人从梯子上摔下来了",
            "description_en": "Help! Someone fell off a ladder in Zone A.",
        },
        "after": ("assistant", "救援马上就到。如果安全，请待在原地。"),
    },
}


def load_seed() -> dict:
    local = ROOT / "seed.local.json"
    return json.loads((local if local.exists() else ROOT / "seed.json").read_text(encoding="utf-8"))


def post(url: str, message: dict) -> dict:
    r = httpx.post(url, json={"message": message}, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("scenario", nargs="?", default="hazard", choices=[*SCENARIOS, "assistant"])
    p.add_argument("--url", default="http://localhost:8000/vapi/webhook")
    p.add_argument("--from", dest="caller", help="caller phone (default: first worker in the roster)")
    a = p.parse_args()

    caller = a.caller or load_seed()["workers"][0]["phone"]
    call = {"id": f"sim-{uuid.uuid4().hex[:8]}", "type": "inboundPhoneCall", "customer": {"number": caller}}

    if a.scenario == "assistant":
        print(json.dumps(post(a.url, {"type": "assistant-request", "call": call}), ensure_ascii=False, indent=2))
        return

    s = SCENARIOS[a.scenario]
    for role, text in s["lines"]:
        post(a.url, {"type": "transcript", "transcriptType": "final", "role": role, "transcript": text, "call": call})
    tool_call = {"id": f"call_{uuid.uuid4().hex[:12]}", "type": "function",
                 "function": {"name": s["tool"], "arguments": s["args"]}}
    out = post(a.url, {"type": "tool-calls", "call": call, "toolCallList": [tool_call]})
    print("tool-calls response:", json.dumps(out, ensure_ascii=False))
    role, text = s["after"]
    post(a.url, {"type": "transcript", "transcriptType": "final", "role": role, "transcript": text, "call": call})
    print("OK. Dashboard: http://localhost:8000")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPError as e:
        sys.exit(f"Request failed: {e}\nIs the server running?  uvicorn app.main:app --port 8000")
