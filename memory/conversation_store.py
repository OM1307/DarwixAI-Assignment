from storage.db import get_conn


def store_conversation(customer_id, message):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversations (customer_id, channel, text, timestamp) VALUES (?, ?, ?, ?)",
        (
            customer_id,
            message.get("channel"),
            message.get("text"),
            message.get("timestamp"),
        ),
    )
    conn.commit()
    conn.close()


def get_conversation(customer_id, limit=50):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT customer_id, channel, text, timestamp FROM conversations WHERE customer_id = ? ORDER BY id DESC LIMIT ?",
        (customer_id, limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return list(reversed(rows))
