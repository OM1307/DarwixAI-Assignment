from transformers import pipeline

sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment"
)

_label_map = {
    "LABEL_0": "NEGATIVE",
    "LABEL_1": "NEUTRAL",
    "LABEL_2": "POSITIVE",
}


def analyze_sentiment(text):
    result = sentiment_model(text)[0]
    label = _label_map.get(result["label"], result["label"])
    return {
        "label": label,
        "score": float(result["score"])
    }
