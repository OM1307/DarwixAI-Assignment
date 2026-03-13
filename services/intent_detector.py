from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

labels = [
    "order issue",
    "payment issue",
    "refund request",
    "delivery delay",
    "cancel order",
    "account access",
    "technical issue",
    "complaint",
    "general inquiry"
]


def _low_signal(text):
    cleaned = "".join([c for c in text if c.isalnum() or c.isspace()]).strip()
    if len(cleaned) < 6:
        return True
    alpha = sum(1 for c in cleaned if c.isalpha())
    ratio = alpha / max(1, len(cleaned))
    if ratio < 0.4:
        return True
    return False


def detect_intent(text):
    text = text or ""
    if _low_signal(text):
        return {
            "label": "general inquiry",
            "score": 0.2,
            "candidates": [{"label": "general inquiry", "score": 0.2}],
            "fallback": "low_signal",
        }

    result = classifier(text, labels)
    top_label = result["labels"][0]
    top_score = float(result["scores"][0])

    if top_score < 0.45:
        top_label = "general inquiry"

    return {
        "label": top_label,
        "score": top_score,
        "candidates": [
            {"label": label, "score": float(score)}
            for label, score in zip(result["labels"], result["scores"])
        ],
    }
