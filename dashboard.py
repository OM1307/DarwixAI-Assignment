import requests
import streamlit as st

st.set_page_config(page_title="CXBrain Resolve", layout="wide")

API_BASE = "http://localhost:8000"


def api_get(path):
    try:
        return requests.get(f"{API_BASE}{path}", timeout=5).json()
    except Exception:
        return None


def api_post(path, payload):
    try:
        return requests.post(f"{API_BASE}{path}", json=payload, timeout=20).json()
    except Exception:
        return None


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

:root {
  --ink: #121519;
  --muted: #6b7280;
  --line: #e6e1d9;
  --card: #ffffff;
  --clay: #c97b5a;
  --teal: #2a6f6f;
  --navy: #1e2a3a;
  --shadow: rgba(18, 21, 25, 0.08);
}

html, body, [class*="css"] { font-family: "Plus Jakarta Sans", sans-serif; color: var(--ink); }
.stApp { background: radial-gradient(circle at 10% 10%, #fdf8f2, #f3ece3 50%, #f6efe7 100%); }

.header {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 18px 22px;
  box-shadow: 0 12px 26px var(--shadow);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-family: "DM Serif Display", serif;
  font-size: 1.6rem;
  color: var(--navy);
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  background: #e7f7f2;
  color: #0f766e;
  font-size: 0.85rem;
  border: 1px solid #c8efe4;
}

.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 10px 22px var(--shadow);
  margin-bottom: 16px;
}

.card.intake {
  background: #ffffff;
}

/* Force Streamlit form container to white */
div[data-testid="stForm"] {
  background: #ffffff !important;
  border: 1px solid var(--line) !important;
  border-radius: 16px !important;
  padding: 16px 18px !important;
  box-shadow: 0 10px 22px var(--shadow) !important;
}

.card h3 {
  margin: 0 0 10px 0;
  font-size: 1rem;
  color: var(--navy);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.metric {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px 12px;
  background: #fbf8f4;
  font-size: 0.85rem;
}

.metric b { display: block; margin-top: 4px; }

.reply-head {
  background: linear-gradient(90deg, var(--navy), var(--teal));
  color: #fff;
  padding: 10px 12px;
  border-radius: 12px 12px 0 0;
  font-weight: 600;
}

.reply-body {
  padding: 12px;
  border: 1px solid var(--line);
  border-top: none;
  border-radius: 0 0 12px 12px;
  background: #fff;
  line-height: 1.6;
}

.action-bar {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.btn {
  background: var(--clay);
  color: #fff;
  padding: 8px 12px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
}

.btn.secondary {
  background: #eef1f5;
  color: var(--ink);
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #e9f4f4;
  color: #1f6f6f;
  font-size: 0.75rem;
}

.kv {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.kv .box {
  background: #fbf8f4;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px;
  text-align: center;
}

.timeline-item {
  padding: 10px 12px;
  border-left: 3px solid var(--teal);
  background: #fff8f1;
  border-radius: 10px;
  margin-bottom: 10px;
}

.note {
  color: var(--muted);
  font-size: 0.85rem;
}
</style>
""",
    unsafe_allow_html=True,
)

health = api_get("/health")
status_text = "Online" if health else "Offline"

st.markdown(
    f"""
<div class="header">
  <div>
    <div class="brand">CXBrain Resolve</div>
    <div class="note">Unified intelligence for omnichannel customer support.</div>
  </div>
  <div class="status">{status_text}</div>
</div>
""",
    unsafe_allow_html=True,
)

customers_payload = api_get("/customers")
customers = customers_payload.get("customers", []) if customers_payload else []

with st.form("intake"):
    st.markdown("<div class='card intake'>", unsafe_allow_html=True)
    st.markdown("<h3>Case Intake</h3>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1.2, 1.2, 1])

    if customers:
        customer_label = col_a.selectbox(
            "Customer",
            [f"{c['customer_id']} - {c['name']}" for c in customers],
            index=0,
        )
        customer_id = customer_label.split(" - ")[0]
        customer_name = customer_label.split(" - ")[1]
    else:
        customer_id = col_a.text_input("Customer ID", value="CUST-1001")
        customer_name = col_b.text_input("Customer Name", value="Ava Patel")

    if customers:
        customer_name = col_b.text_input("Customer Name", value=customer_name)

    channel = col_c.selectbox(
        "Channel",
        ["whatsapp", "email", "webchat", "voice", "social"],
        index=0,
    )

    message = st.text_area(
        "Message",
        height=110,
        placeholder="Paste the latest customer message or call transcript...",
    )

    submit = st.form_submit_button("Analyze")
    st.markdown("</div>", unsafe_allow_html=True)

if submit and message:
    payload = {"customer_id": customer_id, "customer_name": customer_name}
    if channel == "whatsapp":
        payload.update({"phone": customer_id, "message": message})
    elif channel == "email":
        payload.update({"from": customer_id, "body": message})
    elif channel == "webchat":
        payload.update({"user_id": customer_id, "text": message})
    elif channel == "voice":
        payload.update({"caller_id": customer_id, "transcript": message})
    else:
        payload.update({"handle": customer_id, "text": message})

    response = api_post(f"/incoming/{channel}", payload)
    if response and response.get("analysis"):
        st.session_state["analysis"] = response["analysis"]
    else:
        st.error("API response unavailable. Ensure the FastAPI server is running.")

analysis = st.session_state.get("analysis")

if analysis:
    intent = analysis["intent"]
    sentiment = analysis["sentiment"]
    urgency = analysis["urgency"]
    action = analysis["recommended_action"]
    automation = analysis["automation_result"]
    profile = analysis.get("customer_profile")

    left, right = st.columns([2.1, 1])

    with left:
        st.markdown(
            f"""
<div class="card">
  <h3>AI Summary</h3>
  <div class="metric-grid">
    <div class="metric">Intent<b>{intent['label']}</b></div>
    <div class="metric">Sentiment<b>{sentiment['label']}</b></div>
    <div class="metric">Urgency<b>{urgency['level']} / 5</b></div>
    <div class="metric">Action<b>{action['primary_action'].replace('_',' ')}</b></div>
  </div>
  <div class="note" style="margin-top:10px;">Owner: {action['owner']} | ETA: {action['eta_minutes']} min</div>
  <div class="note">Automation: {automation['status']} - {automation['result']}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='card' style='padding:0;'>", unsafe_allow_html=True)
        st.markdown("<div class='reply-head'>Suggested Reply</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='reply-body'>{analysis['ai_reply']}</div></div>", unsafe_allow_html=True)

        if channel in ["whatsapp", "email", "voice"]:
            st.markdown("<div class='action-bar'>", unsafe_allow_html=True)
            send_click = st.button("Send Reply")
            st.markdown("<div class='btn secondary'>Edit</div><div class='btn secondary'>Copy</div></div>", unsafe_allow_html=True)
            if send_click:
                if channel == "whatsapp":
                    send_response = api_post(
                        "/outbound/whatsapp",
                        {"to": analysis["customer_id"], "body": analysis["ai_reply"], "preview_url": False, "dry_run": False},
                    )
                elif channel == "email":
                    send_response = api_post(
                        "/outbound/email",
                        {"to": analysis["customer_id"], "subject": "Support update", "body": analysis["ai_reply"]},
                    )
                else:
                    send_response = api_post(
                        "/outbound/voice",
                        {"to": analysis["customer_id"], "message": analysis["ai_reply"]},
                    )
                st.session_state["send_result"] = send_response.get("result") if send_response else {"status": "error"}

            send_result = st.session_state.get("send_result")
            if send_result:
                st.markdown(
                    f"<div class='card'><div class='note'>Delivery status: {send_result.get('status')} | Details: {send_result.get('reason') or send_result.get('error') or send_result.get('http_status')}</div></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div class='card'><h3>Conversation</h3>", unsafe_allow_html=True)
        timeline = api_get(f"/conversation/{analysis['customer_id']}")
        if timeline and timeline.get("conversation_timeline"):
            recent_msgs = list(reversed(timeline["conversation_timeline"]))[:6]
            for msg in recent_msgs:
                st.markdown(
                    f"<div class='timeline-item'><strong>{msg['channel']}</strong><br>{msg['text']}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='note'>No timeline yet.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        initials = "AP"
        if profile and profile.get("name"):
            parts = profile.get("name").split()
            initials = "".join([p[0] for p in parts[:2]]).upper()
        st.markdown(
            f"""
<div class="card">
  <h3>Customer Snapshot</h3>
  <div class="snapshot-circle">{initials}</div>
  <div style="text-align:center; font-weight:600;">{profile['name'] if profile else 'Customer'}</div>
  <div style="text-align:center; color:#7c7f90;">ID: {profile['customer_id'] if profile else ''}</div>
  <div style="text-align:center; margin-top:8px;"><span class="badge">{profile['segment'] if profile else 'standard'}</span></div>
  <div class="kv">
    <div class="box"><div class="note">Orders</div><div style="font-weight:700;">{profile['orders'] if profile else 0}</div></div>
    <div class="box"><div class="note">Complaints</div><div style="font-weight:700;">{profile['past_complaints'] if profile else 0}</div></div>
    <div class="box"><div class="note">Loyalty</div><div style="font-weight:700; color:#16a34a;">{profile['loyalty_score'] if profile else 0}</div></div>
    <div class="box"><div class="note">Open tickets</div><div style="font-weight:700;">{profile['open_tickets'] if profile else 0}</div></div>
  </div>
  <div style="margin-top:12px;" class="badge">Preferred: {profile['preferred_channel'] if profile else 'n/a'}</div>
</div>
""",
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
<div class="card" style="text-align:center; padding:40px 20px;">
  <div style="font-family: 'DM Serif Display', serif; font-size:1.8rem;">Start a new resolution</div>
  <div class="note" style="margin-top:8px;">Add a message above to generate intent, urgency, and the next best action.</div>
</div>
""",
        unsafe_allow_html=True,
    )
