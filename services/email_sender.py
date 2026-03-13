import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def send_email_message(to_address, subject, body):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_SENDER") or username

    missing = []
    if not host:
        missing.append("SMTP_HOST")
    if not username:
        missing.append("SMTP_USERNAME")
    if not password:
        missing.append("SMTP_PASSWORD")
    if not sender:
        missing.append("SMTP_SENDER")

    if missing:
        return {
            "status": "disabled",
            "reason": "Missing SMTP configuration",
            "missing": missing,
            "timestamp": _now_iso(),
        }

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        return {"status": "sent", "timestamp": _now_iso()}
    except Exception as exc:
        return {"status": "error", "error": str(exc), "timestamp": _now_iso()}
