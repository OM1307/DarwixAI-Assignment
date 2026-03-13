import os
from datetime import datetime, timezone
from typing import Optional

import requests


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def send_whatsapp_text(
    to: str,
    body: str,
    preview_url: bool = False,
    phone_number_id: Optional[str] = None,
    access_token: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    dry_run: bool = False,
):
    phone_number_id = phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    access_token = access_token or os.getenv("WHATSAPP_ACCESS_TOKEN")
    api_base = api_base or os.getenv("WHATSAPP_API_BASE")
    api_version = api_version or os.getenv("WHATSAPP_API_VERSION")

    missing = []
    if not phone_number_id:
        missing.append("WHATSAPP_PHONE_NUMBER_ID")
    if not access_token:
        missing.append("WHATSAPP_ACCESS_TOKEN")
    if not api_base:
        missing.append("WHATSAPP_API_BASE")
    if not api_version:
        missing.append("WHATSAPP_API_VERSION")

    if missing:
        return {
            "status": "disabled",
            "reason": "Missing WhatsApp Cloud API configuration",
            "missing": missing,
            "timestamp": _now_iso(),
        }

    url = f"{api_base.rstrip('/')}/{api_version}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body, "preview_url": preview_url},
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    if dry_run:
        return {
            "status": "dry_run",
            "url": url,
            "payload": payload,
            "timestamp": _now_iso(),
        }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
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
        return {
            "status": "error",
            "error": str(exc),
            "timestamp": _now_iso(),
        }
