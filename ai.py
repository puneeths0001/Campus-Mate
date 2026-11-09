# ai.py - talks to Google Gemini using plain web requests (the "requests" library)
import base64, json, re, time, requests
import streamlit as st

MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]   # tried in this order
URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"

def get_key():
    """Key comes from secrets.toml, or from a box in the sidebar."""
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = ""
    return key or st.sidebar.text_input("Gemini API key", type="password", key="gem_key")

def _call(contents, system=None):
    """Sends the conversation to Gemini. If a model is busy (503) we wait and retry, then try the next model."""
    key = get_key()
    if not key:
        raise RuntimeError("Add your Gemini API key (sidebar box or .streamlit/secrets.toml).")
    body = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    error = ""
    for model in MODELS:
        status = None
        for attempt in range(2):
            try:
                r = requests.post(URL.format(model), headers={"x-goog-api-key": key}, json=body, timeout=90)
                status = r.status_code
            except requests.RequestException as e:
                error = f"{model}: network problem ({type(e).__name__})"
                time.sleep(1)
                continue
            if status == 200:
                try:
                    parts = r.json()["candidates"][0]["content"]["parts"]
                except (KeyError, IndexError):
                    raise RuntimeError("Gemini gave no answer to that (it may have been blocked). Try rephrasing.")
                return "".join(p.get("text", "") for p in parts)
            error = f"{model}: {status} {r.text[:200]}"
            if status in (429, 500, 503):          # busy right now: wait a little and try again
                time.sleep(1.5 * (attempt + 1))
                continue
            break                                   # 404 (unknown model name) etc: go to the next model
        if status in (400, 401, 403):               # bad request or bad key: another model will not fix it
            raise RuntimeError(error)
    raise RuntimeError(error or "Gemini did not answer.")

def ask_gemini(prompt, audio=None, mime="audio/wav"):
    """One question in, one answer out (optionally with an audio clip)."""
    parts = [{"text": prompt}]
    if audio:   # audio is sent as base64 text so Gemini can listen to it
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(audio).decode()}})
    return _call([{"role": "user", "parts": parts}])

def chat_gemini(messages, system):
    """A full conversation. messages: [{'role': 'user'|'assistant', 'sent': text, 'imgs': [(bytes, mime)]}].
    Photos are attached only to the latest user message to keep requests small."""
    messages = messages[-16:]                       # remember the last 16 messages
    last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
    contents = []
    for i, m in enumerate(messages):
        parts = [{"text": m["sent"]}]
        for data, mime in m.get("imgs", []):
            if i == last_user:
                parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}})
            else:
                parts[0]["text"] += " (a photo was attached here)"
        contents.append({"role": "user" if m["role"] == "user" else "model", "parts": parts})
    return _call(contents, system)

def strip_fences(text):
    return re.sub(r"^```[a-zA-Z]*\n?|```$", "", text.strip(), flags=re.M).strip()

def parse_json(text):
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))
