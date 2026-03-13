import json
import os
import sqlite3
from datetime import datetime, timezone

_DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_DB_PATH = os.path.abspath(os.path.join(_DB_DIR, "app.db"))


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_conn():
    os.makedirs(_DB_DIR, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT,
            segment TEXT,
            preferred_channel TEXT,
            loyalty_score INTEGER,
            orders INTEGER,
            past_complaints INTEGER,
            open_tickets INTEGER,
            last_purchase TEXT,
            last_seen TEXT,
            notes TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            channel TEXT,
            text TEXT,
            timestamp TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS metrics (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            status TEXT,
            amount REAL,
            created_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            customer_id TEXT,
            order_id TEXT,
            status TEXT,
            amount REAL,
            created_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            action TEXT,
            status TEXT,
            details TEXT,
            created_at TEXT
        )
        """
    )

    conn.commit()
    _seed_defaults(conn)
    conn.close()


def _seed_defaults(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM customers")
    if cur.fetchone()["c"] == 0:
        customers = [
            (
                "CUST-1001",
                "Ava Patel",
                "gold",
                "whatsapp",
                92,
                8,
                1,
                0,
                "2026-02-21",
                _now_iso(),
                "Prefers concise updates and proactive delivery ETA.",
            ),
            (
                "CUST-2044",
                "Liam Chen",
                "silver",
                "email",
                74,
                3,
                2,
                1,
                "2026-01-11",
                _now_iso(),
                "Needs detailed explanations. Escalate if repeat delays.",
            ),
            (
                "CUST-3110",
                "Noah Ruiz",
                "bronze",
                "webchat",
                56,
                2,
                0,
                0,
                "2026-03-02",
                _now_iso(),
                "First-time support requests; keep tone friendly.",
            ),
        ]
        cur.executemany(
            """
            INSERT INTO customers (
                customer_id, name, segment, preferred_channel, loyalty_score,
                orders, past_complaints, open_tickets, last_purchase, last_seen, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            customers,
        )

    cur.execute("SELECT COUNT(*) as c FROM orders")
    if cur.fetchone()["c"] == 0:
        orders = [
            ("ORD-1001", "CUST-1001", "processing", 120.0, "2026-03-01"),
            ("ORD-2044", "CUST-2044", "shipped", 79.5, "2026-02-10"),
            ("ORD-3110", "CUST-3110", "processing", 39.9, "2026-03-05"),
        ]
        cur.executemany(
            "INSERT INTO orders (order_id, customer_id, status, amount, created_at) VALUES (?, ?, ?, ?, ?)",
            orders,
        )

    cur.execute("SELECT COUNT(*) as c FROM payments")
    if cur.fetchone()["c"] == 0:
        payments = [
            ("PAY-1001", "CUST-1001", "ORD-1001", "pending", 120.0, "2026-03-01"),
            ("PAY-2044", "CUST-2044", "ORD-2044", "paid", 79.5, "2026-02-10"),
            ("PAY-3110", "CUST-3110", "ORD-3110", "paid", 39.9, "2026-03-05"),
        ]
        cur.executemany(
            "INSERT INTO payments (payment_id, customer_id, order_id, status, amount, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            payments,
        )

    defaults = {
        "total_messages": 0,
        "avg_urgency": 0.0,
        "by_intent": {},
        "by_sentiment": {},
    }
    cur.execute("SELECT COUNT(*) as c FROM metrics")
    if cur.fetchone()["c"] == 0:
        for k, v in defaults.items():
            cur.execute("INSERT INTO metrics (key, value) VALUES (?, ?)", (k, json.dumps(v)))

    conn.commit()


init_db()
