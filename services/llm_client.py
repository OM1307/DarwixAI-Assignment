import os
import requests


OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")


def _extract_output_text(response_json):
    if "output_text" in response_json:
        return response_json.get("output_text")
    output = response_json.get("output", [])
    chunks = []
    for item in output:
        content = item.get("content", []) if isinstance(item, dict) else []
        for block in content:
            if isinstance(block, dict) and block.get("type") in ["output_text", "text"]:
                chunks.append(block.get("text", ""))
    return "\n".join([c for c in chunks if c]).strip()


def generate_llm_reply(system_prompt, user_prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, "missing_api_key"

    payload = {
        "model": OPENAI_MODEL,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            f"{OPENAI_API_BASE}/responses",
            json=payload,
            headers=headers,
            timeout=25,
        )
        if response.status_code >= 300:
            return None, f"http_{response.status_code}"
        data = response.json()
        text = _extract_output_text(data)
        return text or None, None
    except Exception as exc:
        return None, str(exc)
