from fastapi import FastAPI
from typing import Dict, Optional
from pydantic import BaseModel

# AI Services
from services.intent_detector import detect_intent
from services.sentiment_analyzer import analyze_sentiment
from services.urgency_predictor import predict_urgency
from services.next_action_engine import recommend_action
from services.reply_generator import generate_reply
from services.action_executor import execute_action
from services.whatsapp_sender import send_whatsapp_text
from services.email_sender import send_email_message
from services.voice_sender import place_voice_call

# Memory
from memory.vector_store import store_message
from memory.retrieval import retrieve_history
from memory.conversation_store import store_conversation, get_conversation
from memory.customer_store import list_customers, get_customer, upsert_customer, record_interaction
from memory.metrics_store import record_metrics, get_metrics

# Channel normalization
from channels.channel_router import normalize_message

app = FastAPI(
    title="AI Customer Brain",
    description="Omnichannel AI platform for intelligent customer support",
    version="1.0"
)


class CustomerUpdate(BaseModel):
    customer_id: str
    name: Optional[str] = None


class WhatsAppSendRequest(BaseModel):
    to: str
    body: str
    preview_url: bool = False
    dry_run: bool = False


class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str


class VoiceSendRequest(BaseModel):
    to: str
    message: str


# ---------------------------------------------------
# Root endpoint
# ---------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "AI Customer Brain API Running",
        "channels_supported": [
            "whatsapp",
            "email",
            "webchat",
            "voice",
            "social"
        ]
    }


# ---------------------------------------------------
# Core AI processing pipeline
# ---------------------------------------------------

def process_message(msg: Dict):

    text = msg["text"]
    customer_id = msg["customer_id"]
    customer_name = msg.get("customer_name")

    # Ensure customer exists
    customer_profile = upsert_customer(customer_id, customer_name)

    # 1. Detect intent
    intent = detect_intent(text)

    # 2. Sentiment analysis
    sentiment = analyze_sentiment(text)

    # 3. Retrieve customer history
    history = retrieve_history(customer_id, text)

    # 4. Predict urgency
    urgency = predict_urgency(
        sentiment,
        intent["label"],
        customer_profile,
        msg["channel"],
        history
    )

    # 5. Recommend next best action
    action = recommend_action(intent["label"], urgency, customer_profile)

    # 6. Execute automation
    automation_result = execute_action(action, customer_id)

    # 7. Generate AI reply
    reply = generate_reply(intent, sentiment, history, customer_profile, urgency, action)

    # 8. Store conversation in vector memory
    store_message(
        customer_id,
        text,
        metadata={
            "channel": msg["channel"],
            "intent": intent["label"],
            "sentiment": sentiment["label"],
        }
    )

    # 9. Update customer profile + metrics
    customer_profile = record_interaction(
        customer_id,
        intent["label"],
        sentiment["label"],
        msg["channel"]
    )
    record_metrics(intent["label"], sentiment["label"], urgency["level"])

    return {
        "customer_id": customer_id,
        "channel": msg["channel"],
        "customer_profile": customer_profile,
        "intent": intent,
        "sentiment": sentiment,
        "urgency": urgency,
        "recommended_action": action,
        "automation_result": automation_result,
        "ai_reply": reply,
        "customer_history": history
    }


# ---------------------------------------------------
# Omnichannel incoming messages
# ---------------------------------------------------

@app.post("/incoming/{channel}")
def incoming_message(channel: str, data: Dict):

    # Normalize different channel formats
    msg = normalize_message(data, channel)

    customer_id = msg["customer_id"]

    # Store conversation timeline
    store_conversation(customer_id, msg)

    # Run AI pipeline
    result = process_message(msg)

    # Return unified response
    return {
        "status": "processed",
        "analysis": result
    }


# ---------------------------------------------------
# Customer profile endpoints
# ---------------------------------------------------

@app.get("/customers")
def customers_list():
    return {"customers": list_customers()}


@app.get("/customers/{customer_id}")
def customer_profile(customer_id: str):
    return {"customer": get_customer(customer_id)}


@app.post("/customers")
def customer_upsert(payload: CustomerUpdate):
    return {"customer": upsert_customer(payload.customer_id, payload.name)}


# ---------------------------------------------------
# Outbound messaging
# ---------------------------------------------------

@app.post("/outbound/whatsapp")
def outbound_whatsapp(payload: WhatsAppSendRequest):
    result = send_whatsapp_text(
        to=payload.to,
        body=payload.body,
        preview_url=payload.preview_url,
        dry_run=payload.dry_run,
    )
    return {"result": result}


@app.post("/outbound/email")
def outbound_email(payload: EmailSendRequest):
    result = send_email_message(payload.to, payload.subject, payload.body)
    return {"result": result}


@app.post("/outbound/voice")
def outbound_voice(payload: VoiceSendRequest):
    result = place_voice_call(payload.to, payload.message)
    return {"result": result}


# ---------------------------------------------------
# Retrieve full conversation timeline
# ---------------------------------------------------

@app.get("/conversation/{customer_id}")
def conversation_history(customer_id: str):

    timeline = get_conversation(customer_id)

    return {
        "customer_id": customer_id,
        "conversation_timeline": timeline
    }


# ---------------------------------------------------
# Metrics endpoint
# ---------------------------------------------------

@app.get("/metrics")
def metrics_snapshot():
    return {"metrics": get_metrics()}


# ---------------------------------------------------
# Health check endpoint
# ---------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "AI Customer Brain is running"}
