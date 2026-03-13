from services.llm_client import generate_llm_reply


def _template_reply(intent_label, sentiment, history, customer_profile, urgency, action_plan):
    customer_name = customer_profile.get("name") or "there"
    tone = "apologetic" if sentiment["label"] == "NEGATIVE" else "professional"
    history_hint = "I see you reached out about similar issues recently. " if history else ""

    if intent_label == "delivery delay":
        body = "I am checking the latest delivery status and confirming a fresh ETA."
    elif intent_label == "payment issue":
        body = "I am reviewing the payment status and will confirm the transaction outcome."
    elif intent_label == "refund request":
        body = "I can start the refund process and will update you once the order is verified."
    elif intent_label == "complaint":
        body = "I am escalating this to our support lead to resolve quickly."
    elif intent_label == "cancel order":
        body = "I can cancel this order and confirm once it is processed."
    elif intent_label == "account access":
        body = "I can help restore access after a quick identity check."
    elif intent_label == "technical issue":
        body = "I can troubleshoot this and collect details to resolve it faster."
    else:
        body = "I can help with that and will share the best next steps."

    urgency_line = ""
    if urgency["level"] >= 4:
        urgency_line = "I am prioritizing this as urgent and will update you shortly. "

    closing = "Is there anything else you want me to check?"
    if tone == "apologetic":
        closing = "Thank you for your patience. " + closing

    return (
        f"Hi {customer_name}, "
        f"{history_hint}"
        f"{urgency_line}"
        f"{body} "
        f"Next, I will {action_plan['primary_action'].replace('_', ' ')}. "
        f"{closing}"
    )


def generate_reply(intent, sentiment, history, customer_profile, urgency, action_plan):
    intent_label = intent["label"] if isinstance(intent, dict) else intent

    system_prompt = (
        "You are a customer support assistant. "
        "Write a concise, professional reply in 3-5 sentences. "
        "Avoid promises you cannot keep. "
        "Do not ask more than one question. "
        "Keep the tone empathetic if sentiment is negative."
    )

    user_prompt = (
        f"Customer name: {customer_profile.get('name')}\n"
        f"Channel: {customer_profile.get('preferred_channel')}\n"
        f"Intent: {intent_label}\n"
        f"Sentiment: {sentiment['label']}\n"
        f"Urgency: {urgency['level']} (reasons: {', '.join(urgency['reasons'])})\n"
        f"Action plan: {action_plan['primary_action']} with {', '.join(action_plan['secondary_actions'])}\n"
        f"History snippets: {history}\n"
        "Write the response message."
    )

    llm_text, error = generate_llm_reply(system_prompt, user_prompt)
    if llm_text:
        return llm_text

    return _template_reply(intent_label, sentiment, history, customer_profile, urgency, action_plan)
