from datetime import datetime, timezone
import random

from services.order_actions import cancel_latest_order
from services.payment_actions import refund_latest_payment, verify_latest_payment


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def execute_action(action_plan, customer_id=None):
    primary = action_plan["primary_action"]
    ticket_id = f"TCK-{random.randint(10000, 99999)}"

    if primary == "trigger_refund":
        refund = refund_latest_payment(customer_id) if customer_id else {"status": "skipped"}
        return {
            "status": "automated",
            "result": f"Refund workflow started ({refund.get('status')})",
            "ticket_id": ticket_id,
            "timestamp": _now_iso(),
            "details": refund,
        }

    if primary == "verify_payment":
        verification = verify_latest_payment(customer_id) if customer_id else {"status": "skipped"}
        return {
            "status": "automated",
            "result": f"Payment verification started ({verification.get('status')})",
            "ticket_id": ticket_id,
            "timestamp": _now_iso(),
            "details": verification,
        }

    if primary in ["expedite_delivery", "check_delivery_status"]:
        return {
            "status": "automated",
            "result": "Logistics workflow queued",
            "ticket_id": ticket_id,
            "timestamp": _now_iso(),
        }

    if primary in ["escalate_manager", "create_case"]:
        return {
            "status": "escalated",
            "result": "Case routed to support",
            "ticket_id": ticket_id,
            "timestamp": _now_iso(),
        }

    if primary == "cancel_order":
        cancel_result = cancel_latest_order(customer_id) if customer_id else {"status": "skipped"}
        return {
            "status": "automated",
            "result": f"Order cancellation requested ({cancel_result.get('status')})",
            "ticket_id": ticket_id,
            "timestamp": _now_iso(),
            "details": cancel_result,
        }

    if primary == "reset_access":
        return {
            "status": "automated",
            "result": "Account recovery started",
            "ticket_id": ticket_id,
            "timestamp": _now_iso(),
        }

    if primary == "collect_diagnostics":
        return {
            "status": "recommended",
            "result": "Diagnostic checklist prepared",
            "ticket_id": ticket_id,
            "timestamp": _now_iso(),
        }

    return {
        "status": "recommended",
        "result": "Action recommended to agent",
        "ticket_id": ticket_id,
        "timestamp": _now_iso(),
    }
