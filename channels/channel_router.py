from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def normalize_message(data, channel):

    if channel == "whatsapp":

        return {
            "customer_id": data.get("customer_id") or data.get("phone") or "unknown",
            "customer_name": data.get("customer_name"),
            "channel": "whatsapp",
            "text": data.get("message") or data.get("text") or "",
            "timestamp": data.get("timestamp") or _now_iso()
        }

    elif channel == "email":

        return {
            "customer_id": data.get("customer_id") or data.get("from") or "unknown",
            "customer_name": data.get("customer_name"),
            "channel": "email",
            "text": data.get("body") or data.get("text") or "",
            "timestamp": data.get("timestamp") or _now_iso()
        }

    elif channel == "webchat":

        return {
            "customer_id": data.get("customer_id") or data.get("user_id") or "unknown",
            "customer_name": data.get("customer_name"),
            "channel": "chat",
            "text": data.get("text") or "",
            "timestamp": data.get("timestamp") or _now_iso()
        }

    elif channel == "voice":

        return {
            "customer_id": data.get("customer_id") or data.get("caller_id") or "unknown",
            "customer_name": data.get("customer_name"),
            "channel": "voice",
            "text": data.get("transcript") or data.get("text") or "",
            "timestamp": data.get("timestamp") or _now_iso()
        }

    elif channel == "social":

        return {
            "customer_id": data.get("customer_id") or data.get("handle") or "unknown",
            "customer_name": data.get("customer_name"),
            "channel": "social",
            "text": data.get("text") or data.get("post") or "",
            "timestamp": data.get("timestamp") or _now_iso()
        }

    else:

        return {
            "customer_id": data.get("customer_id") or "unknown",
            "customer_name": data.get("customer_name"),
            "channel": channel,
            "text": data.get("text") if isinstance(data, dict) else str(data),
            "timestamp": _now_iso()
        }
