def recommend_action(intent, urgency, customer_profile):

    level = urgency["level"]
    segment = customer_profile.get("segment")
    owner = "support"
    eta_minutes = 120

    if intent == "refund request":
        primary = "trigger_refund"
        secondary = ["verify_order", "send_refund_status"]
        owner = "billing"
        eta_minutes = 60
    elif intent == "payment issue":
        primary = "verify_payment"
        secondary = ["open_payment_case", "request_transaction_id"]
        owner = "payments"
        eta_minutes = 30 if level >= 4 else 90
    elif intent == "delivery delay":
        primary = "expedite_delivery" if level >= 4 else "check_delivery_status"
        secondary = ["notify_logistics", "share_eta"]
        owner = "logistics"
        eta_minutes = 45 if level >= 4 else 120
    elif intent == "complaint":
        primary = "escalate_manager" if level >= 3 else "create_case"
        secondary = ["collect_details", "offer_credit"]
        owner = "support_manager" if level >= 3 else "support"
        eta_minutes = 30 if level >= 4 else 180
    elif intent == "cancel order":
        primary = "cancel_order"
        secondary = ["confirm_cancellation", "offer_alternative"]
        owner = "operations"
        eta_minutes = 30
    elif intent == "account access":
        primary = "reset_access"
        secondary = ["verify_identity", "secure_account"]
        owner = "security"
        eta_minutes = 20 if level >= 4 else 60
    elif intent == "technical issue":
        primary = "collect_diagnostics"
        secondary = ["create_ticket", "share_troubleshooting"]
        owner = "tech_support"
        eta_minutes = 90
    else:
        primary = "provide_information"
        secondary = ["share_help_center", "offer_follow_up"]
        owner = "support"
        eta_minutes = 240

    if segment == "gold":
        eta_minutes = max(15, int(eta_minutes * 0.6))

    return {
        "primary_action": primary,
        "secondary_actions": secondary,
        "owner": owner,
        "eta_minutes": eta_minutes,
        "playbook": f"{intent}-standard",
    }
