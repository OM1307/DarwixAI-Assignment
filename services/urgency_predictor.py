def predict_urgency(sentiment, intent, customer_profile, channel, history):

    score = 1
    reasons = []

    if sentiment["label"] == "NEGATIVE":
        score += 2
        reasons.append("Negative sentiment detected")
    elif sentiment["label"] == "NEUTRAL":
        score += 1
        reasons.append("Neutral sentiment requires prompt clarity")

    if intent in ["complaint", "delivery delay"]:
        score += 2
        reasons.append("Intent indicates service risk")

    if intent in ["payment issue", "account access"]:
        score += 2
        reasons.append("Critical access or payment impact")

    if intent == "refund request":
        score += 1
        reasons.append("Refund requests impact revenue")

    if channel in ["social", "voice"]:
        score += 1
        reasons.append("High visibility or live channel")

    if customer_profile.get("segment") == "gold":
        score += 1
        reasons.append("High value customer")

    if customer_profile.get("open_tickets", 0) > 0:
        score += 1
        reasons.append("Existing open ticket")

    if history:
        score += 1
        reasons.append("Similar issue detected in history")

    score = min(score, 5)
    sla_risk = "high" if score >= 4 else "medium" if score == 3 else "low"

    return {
        "level": score,
        "sla_risk": sla_risk,
        "reasons": reasons
    }
