from storage.db import get_conn


def cancel_latest_order(customer_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT order_id, status FROM orders
        WHERE customer_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (customer_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"status": "not_found", "message": "No orders found"}

    if row["status"] == "cancelled":
        conn.close()
        return {"status": "no_change", "message": "Order already cancelled", "order_id": row["order_id"]}

    cur.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?",
        ("cancelled", row["order_id"]),
    )
    conn.commit()
    conn.close()
    return {"status": "cancelled", "order_id": row["order_id"]}
