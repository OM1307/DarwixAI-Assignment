from storage.db import get_conn


def verify_latest_payment(customer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT payment_id, status FROM payments
        WHERE customer_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (customer_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"status": "not_found", "message": "No payments found"}

    if row["status"] in ["paid", "verified"]:
        conn.close()
        return {"status": "no_change", "message": "Payment already verified", "payment_id": row["payment_id"]}

    cur.execute(
        "UPDATE payments SET status = ? WHERE payment_id = ?",
        ("verified", row["payment_id"]),
    )
    conn.commit()
    conn.close()
    return {"status": "verified", "payment_id": row["payment_id"]}


def refund_latest_payment(customer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT payment_id, status, order_id FROM payments
        WHERE customer_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (customer_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"status": "not_found", "message": "No payments found"}

    if row["status"] == "refunded":
        conn.close()
        return {"status": "no_change", "message": "Already refunded", "payment_id": row["payment_id"]}

    cur.execute(
        "UPDATE payments SET status = ? WHERE payment_id = ?",
        ("refunded", row["payment_id"]),
    )
    if row["order_id"]:
        cur.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            ("refunded", row["order_id"]),
        )

    conn.commit()
    conn.close()
    return {"status": "refunded", "payment_id": row["payment_id"], "order_id": row["order_id"]}
