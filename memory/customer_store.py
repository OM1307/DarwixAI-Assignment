from datetime import datetime, timezone

from storage.db import get_conn


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def list_customers():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers ORDER BY name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_customer(customer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_customer(customer_id, name=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    row = cur.fetchone()

    if row:
        if name:
            cur.execute(
                "UPDATE customers SET name = ?, last_seen = ? WHERE customer_id = ?",
                (name, _now_iso(), customer_id),
            )
        else:
            cur.execute(
                "UPDATE customers SET last_seen = ? WHERE customer_id = ?",
                (_now_iso(), customer_id),
            )
    else:
        cur.execute(
            """
            INSERT INTO customers (
                customer_id, name, segment, preferred_channel, loyalty_score,
                orders, past_complaints, open_tickets, last_purchase, last_seen, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                name or "Unknown",
                "standard",
                "email",
                50,
                0,
                0,
                0,
                None,
                _now_iso(),
                "",
            ),
        )

    conn.commit()
    cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row)


def record_interaction(customer_id, intent, sentiment_label, channel):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return upsert_customer(customer_id)

    preferred = channel or row["preferred_channel"]
    cur.execute(
        "UPDATE customers SET last_seen = ?, preferred_channel = ? WHERE customer_id = ?",
        (_now_iso(), preferred, customer_id),
    )
    conn.commit()
    cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row)
