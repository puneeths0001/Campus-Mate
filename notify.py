# notify.py - talks to a Telegram bot (free) so the student and parent can exchange messages
import requests
import streamlit as st

def _token():
    try:
        return st.secrets["TELEGRAM_BOT_TOKEN"]
    except Exception:
        return ""

@st.cache_resource
def _store():
    """Server memory that remembers which chat belongs to the parent and the student."""
    return {}

def api(method, **params):
    """Calls the Telegram Bot API. Returns (True/False, result or error text)."""
    token = _token()
    if not token:
        return False, "Add TELEGRAM_BOT_TOKEN to .streamlit/secrets.toml"
    try:
        data = requests.post(f"https://api.telegram.org/bot{token}/{method}", json=params, timeout=20).json()
    except Exception as e:
        return False, str(e)
    return data.get("ok", False), data.get("result", data.get("description", ""))

def chat_id(role):
    """role is 'parent' or 'student'. A fixed id in secrets wins, otherwise the one we linked."""
    try:
        return int(st.secrets[f"TELEGRAM_{role.upper()}_CHAT_ID"])
    except Exception:
        return _store().get(role)

def link(role):
    """Looks in the bot's recent messages for '/start parent' (or student) and remembers that chat."""
    ok, updates = api("getUpdates")
    if not ok:
        return False
    for u in reversed(updates):
        m = u.get("message", {})
        if m.get("text", "").strip() == f"/start {role}":
            _store()[role] = m["chat"]["id"]
            return True
    return False

def link_widget(role, who):
    """Shows the one-time connect steps. Returns True when this person is connected."""
    if chat_id(role):
        st.success(f"{who} is connected on Telegram.")
        return True
    ok, bot = api("getMe")
    if ok:
        url = f"https://t.me/{bot['username']}?start={role}"
        st.markdown(f"**{who}:** open [{url}]({url}) on Telegram, tap **Start**, then press the button below.")
    else:
        st.error(bot)
    if st.button(f"I pressed Start ({who})", key=f"link_{role}"):
        if link(role):
            st.rerun()
        st.warning("Nothing found yet. Press Start in Telegram first, then try again.")
    return False

def send_message(role, text):
    cid = chat_id(role)
    return api("sendMessage", chat_id=cid, text=text) if cid else (False, f"{role} is not connected yet")

def send_location(role, lat, lon):
    """Sends a LIVE location pin (stays on the map for 4 hours) and remembers it so we can move it."""
    cid = chat_id(role)
    if not cid:
        return False, f"{role} is not connected yet"
    ok, res = api("sendLocation", chat_id=cid, latitude=lat, longitude=lon, live_period=14400)
    if ok:
        _store()["live_msg"] = res["message_id"]
    return ok, res

def update_live(role, lat, lon):
    """Moves the existing live pin. Returns False if there is none yet."""
    mid, cid = _store().get("live_msg"), chat_id(role)
    if not (mid and cid):
        return False
    return api("editMessageLiveLocation", chat_id=cid, message_id=mid, latitude=lat, longitude=lon)[0]

def replies(role, n=5):
    """Last few text messages the person sent to the bot (the parent's replies)."""
    cid = chat_id(role)
    ok, updates = api("getUpdates")
    if not (ok and cid):
        return []
    texts = [u["message"]["text"] for u in updates
             if u.get("message", {}).get("chat", {}).get("id") == cid
             and not u["message"].get("text", "/").startswith("/")]
    return texts[-n:]
