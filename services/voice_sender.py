import os
from datetime import datetime, timezone

import requests


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def place_voice_call(to_number, message):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")

    missing = []
    if not account_sid:
        missing.append("TWILIO_ACCOUNT_SID")
    if not auth_token:
        missing.append("TWILIO_AUTH_TOKEN")
    if not from_number:
        missing.append("TWILIO_FROM_NUMBER")

    if missing:
        return {
            "status": "disabled",
            "reason": "Missing Twilio Voice configuration",
            "missing": missing,
            "timestamp": _now_iso(),
        }

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    payload = {
        "To": to_number,
        "From": from_number,
        "Twiml": f"<Response><Say>{message}</Say></Response>",
    }

    try:
        response = requests.post(url, data=payload, auth=(account_sid, auth_token), timeout=20)
        ok = response.status_code < 300
        try:
            body_json = response.json()
        except Exception:
            body_json = {"raw": response.text}
        return {
            "status": "sent" if ok else "failed",
            "http_status": response.status_code,
            "response": body_json,
            "timestamp": _now_iso(),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc), "timestamp": _now_iso()}
