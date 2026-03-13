import json
from datetime import datetime, timezone

from storage.db import get_conn


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _get_metric(cur, key, default):
    cur.execute("SELECT value FROM metrics WHERE key = ?", (key,))
    row = cur.fetchone()
    if not row:
        return default
    try:
        return json.loads(row["value"])
    except Exception:
        return default


def _set_metric(cur, key, value):
    cur.execute(
        "INSERT INTO metrics (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, json.dumps(value)),
    )


def record_metrics(intent, sentiment_label, urgency):
    conn = get_conn()
    cur = conn.cursor()

    total = _get_metric(cur, "total_messages", 0) + 1
    avg = _get_metric(cur, "avg_urgency", 0.0)
    by_intent = _get_metric(cur, "by_intent", {})
    by_sentiment = _get_metric(cur, "by_sentiment", {})

    by_intent[intent] = by_intent.get(intent, 0) + 1
    by_sentiment[sentiment_label] = by_sentiment.get(sentiment_label, 0) + 1
    avg = round((avg * (total - 1) + urgency) / total, 2)

    _set_metric(cur, "total_messages", total)
    _set_metric(cur, "avg_urgency", avg)
    _set_metric(cur, "by_intent", by_intent)
    _set_metric(cur, "by_sentiment", by_sentiment)
    _set_metric(cur, "last_updated", _now_iso())

    conn.commit()
    conn.close()


def get_metrics():
    conn = get_conn()
    cur = conn.cursor()
    metrics = {
        "total_messages": _get_metric(cur, "total_messages", 0),
        "avg_urgency": _get_metric(cur, "avg_urgency", 0.0),
        "by_intent": _get_metric(cur, "by_intent", {}),
        "by_sentiment": _get_metric(cur, "by_sentiment", {}),
        "last_updated": _get_metric(cur, "last_updated", None),
    }
    conn.close()
    return metrics
