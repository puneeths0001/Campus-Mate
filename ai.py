# ai.py - talks to Google Gemini using plain web requests (the "requests" library)
import base64, json, re, time, requests
import streamlit as st

# (model name, extra settings). "Low thinking" makes answers start much faster.
MODELS = [
    ("gemini-3.8-flash", {"thinkingConfig": {"thinkingLevel": "low"}}),
    ("gemini-2.5-flash", {"thinkingConfig": {"thinkingBudget": 0}}),
    ("gemini-2.5-flash-lite", {}),
]
URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
STREAM_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:streamGenerateContent?alt=sse"

def get_key():
    """Key comes from secrets.toml, or from a box in the sidebar."""
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = ""
    return key or st.sidebar.text_input("Gemini API key", type="password", key="gem_key")

def _body(contents, system, gen):
    body = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if gen:
        body["generationConfig"] = gen
    return body

def _need_key():
    key = get_key()
    if not key:
        raise RuntimeError("Add your Gemini API key (sidebar box or .streamlit/secrets.toml).")
    return key

def _call(contents, system=None):
    """Sends the conversation to Gemini and waits for the whole answer. Busy model (503): wait, retry, then try the next model."""
    key = _need_key()
    error = ""
    for model, gen in MODELS:
        status, use_gen = None, True
        for attempt in range(2):
            try:
                r = requests.post(URL.format(model), headers={"x-goog-api-key": key},
                                  json=_body(contents, system, gen if use_gen else None), timeout=90)
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
                return "".join(p.get("text", "") for p in parts if not p.get("thought"))
            error = f"{model}: {status} {r.text[:200]}"
            if status == 400 and gen and use_gen and "thinking" in r.text.lower():
                use_gen = False                      # this model dislikes the thinking setting: retry without it
                continue
            if status in (429, 500, 503):            # busy right now: wait a little and try again
                time.sleep(1.5 * (attempt + 1))
                continue
            break                                    # 404 (unknown model name) etc: go to the next model
        if status in (400, 401, 403):                # bad request or bad key: another model will not fix it
            raise RuntimeError(error)
    raise RuntimeError(error or "Gemini did not answer.")

def stream_gemini(contents, system=None):
    """Like _call, but gives the answer in small pieces as Gemini writes it, so the first words appear quickly."""
    key = _need_key()
    error = ""
    for model, gen in MODELS:
        status, use_gen = None, True
        for attempt in range(2):
            try:
                r = requests.post(STREAM_URL.format(model), headers={"x-goog-api-key": key},
                                  json=_body(contents, system, gen if use_gen else None),
                                  timeout=(10, 120), stream=True)
                status = r.status_code
            except requests.RequestException as e:
                error = f"{model}: network problem ({type(e).__name__})"
                time.sleep(1)
                continue
            if status == 200:
                r.encoding = "utf-8"
                got = False
                for line in r.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data:"):
                        continue
                    try:
                        chunk = json.loads(line[5:].strip())
                    except ValueError:
                        continue
                    for cand in chunk.get("candidates", []):
                        for p in cand.get("content", {}).get("parts", []):
                            if p.get("text") and not p.get("thought"):
                                got = True
                                yield p["text"]
                if not got:
                    raise RuntimeError("Gemini gave no answer to that (it may have been blocked). Try rephrasing.")
                return
            error = f"{model}: {status} {r.text[:200]}"
            if status == 400 and gen and use_gen and "thinking" in r.text.lower():
                use_gen = False
                continue
            if status in (429, 500, 503):
                time.sleep(1.5 * (attempt + 1))
                continue
            break
        if status in (400, 401, 403):
            raise RuntimeError(error)
    raise RuntimeError(error or "Gemini did not answer.")

def ask_gemini(prompt, audio=None, mime="audio/wav"):
    """One question in, one answer out (optionally with an audio clip)."""
    parts = [{"text": prompt}]
    if audio:   # audio is sent as base64 text so Gemini can listen to it
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(audio).decode()}})
    return _call([{"role": "user", "parts": parts}])

def _chat_contents(messages):
    """messages: [{'role': 'user'|'assistant', 'sent': text, 'imgs': [(bytes, mime)]}]. Photos go only with the latest user message."""
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
    return contents

def chat_gemini(messages, system):
    return _call(_chat_contents(messages), system)

def chat_stream(messages, system):
    return stream_gemini(_chat_contents(messages), system)

def strip_fences(text):
    return re.sub(r"^```[a-zA-Z]*\n?|```$", "", text.strip(), flags=re.M).strip()

def parse_json(text):
    return json.loads(re.search(r"\{.*\}", text, re.S).group(0))
