# ai.py - talks to Google Gemini using plain web requests (the "requests" library)
import base64, json, re, requests
import streamlit as st

MODELS = ["gemini-3.8-flash", "gemini-2.5-flash"]   # tries the first, falls back to the second

def get_key():
    """Key comes from secrets.toml, or from a box in the sidebar."""
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = ""
    return key or st.sidebar.text_input("Gemini API key", type="password", key="gem_key")

def ask_gemini(prompt, audio=None, mime="audio/wav"):
    key = get_key()
    if not key:
        raise RuntimeError("Add your Gemini API key (sidebar box or .streamlit/secrets.toml).")
    parts = [{"text": prompt}]
    if audio:   # audio is sent as base64 text so Gemini can listen to it
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(audio).decode()}})
    error = ""
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        r = requests.post(url, headers={"x-goog-api-key": key},
                          json={"contents": [{"parts": parts}]}, timeout=90)
        if r.status_code == 200:
            out = r.json()["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in out)
        error = f"{model}: {r.status_code} {r.text[:200]}"
        if r.status_code != 404:       # 404 = model name not found, so try the next one
            break
    raise RuntimeError(error)

def strip_fences(text):
    return re.sub(r"^```[a-zA-Z]*\n?|```$", "", text.strip(), flags=re.M).strip()

def parse_json(text):
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))
