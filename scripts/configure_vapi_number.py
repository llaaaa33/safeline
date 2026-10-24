"""Point the Vapi phone number at this backend and detach any fixed assistant,
so every inbound call sends `assistant-request` here. Re-run when the tunnel URL changes.

    python scripts/configure_vapi_number.py

By hand instead: Vapi dashboard -> Phone Numbers -> your number -> remove assistant, set Server URL.
"""
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("VAPI_API_KEY", "").strip()
NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID", "").strip()
BASE = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
if not (KEY and NUMBER_ID and BASE):
    sys.exit("Set VAPI_API_KEY, VAPI_PHONE_NUMBER_ID and PUBLIC_BASE_URL in .env first.")

url = f"https://api.vapi.ai/phone-number/{NUMBER_ID}"
headers = {"Authorization": f"Bearer {KEY}"}
server_url = f"{BASE}/vapi/webhook"

r = httpx.get(url, headers=headers, timeout=15)
if r.status_code >= 300:
    sys.exit(f"Could not read phone number: {r.status_code} {r.text[:300]}")
number = r.json()
print(f"Number {number.get('number')} (provider {number.get('provider')}), assistantId={number.get('assistantId')}")

r = httpx.patch(url, headers=headers, json={"server": {"url": server_url}, "assistantId": None}, timeout=15)
if r.status_code >= 300:
    print(f"PATCH with assistantId=null failed ({r.status_code}): {r.text[:300]}\nRetrying with the server URL only...")
    r = httpx.patch(url, headers=headers, json={"server": {"url": server_url}}, timeout=15)
if r.status_code >= 300:
    sys.exit(f"Update failed: {r.status_code} {r.text[:300]}")

after = r.json()
print(f"Server URL -> {(after.get('server') or {}).get('url')}")
if after.get("assistantId"):
    print("WARNING: an assistant is still attached. Remove it in the Vapi dashboard, "
          "otherwise Vapi won't ask this backend for the per-caller assistant.")
else:
    print("Done. Inbound calls now ask this backend for an assistant.")
