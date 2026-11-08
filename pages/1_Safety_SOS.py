# pages/1_Safety_SOS.py - SOS alert and live location sent to the parent on Telegram
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_geolocation import streamlit_geolocation
from streamlit_autorefresh import st_autorefresh
from theme import apply_theme
from ai import ask_gemini, parse_json
from notify import link_widget, send_message, send_location, update_live, replies

st.set_page_config(page_title="Safety | Campus Mate", page_icon="🚨", layout="wide")
apply_theme()

@st.cache_resource
def shared():
    """Memory shared by every visitor while the server runs (used by the optional web parent view)."""
    return {"locations": [], "alerts": []}
box = shared()

# ---------- Optional web view for parents: open this page with ?parent=1 at the end of the link ----------
if st.query_params.get("parent"):
    st_autorefresh(interval=30000, key="parent_refresh")
    st.title("👨‍👩‍👧 Parent view")
    if box["alerts"]:
        a = box["alerts"][-1]
        st.error(f"🚨 EMERGENCY at {a['time']} ({a['reason']}). Map: {a['link']}")
    if box["locations"]:
        df = pd.DataFrame(box["locations"])
        st.metric("Last seen", df.iloc[-1]["time"])
        st.map(df[["lat", "lon"]])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("The student has not shared location yet.")
    st.stop()

# ---------- Student view ----------
st.title("🚨 Safety")
st.write("**Step 0.** Connect your parent's Telegram (one time only).")
parent_ok = link_widget("parent", "Parent")

st.write("**Step 1.** Tap the target button and allow location in your browser.")
loc = streamlit_geolocation()
has_loc = bool(loc and loc.get("latitude"))

def log_location():
    box["locations"].append({"time": f"{datetime.now():%d %b %H:%M:%S}",
                             "lat": loc["latitude"], "lon": loc["longitude"]})

share = st.toggle("Share my live location with my parents (updates every 5 minutes)")
if share and has_loc:
    st_autorefresh(interval=300000, key="share_refresh")   # re-runs this page every 5 minutes
    if (datetime.now() - box.get("last_log", datetime.min)).total_seconds() > 240:
        log_location()
        box["last_log"] = datetime.now()
        if parent_ok and not update_live("parent", loc["latitude"], loc["longitude"]):
            send_location("parent", loc["latitude"], loc["longitude"])   # first time: start the live pin
    st.success("Sharing is on." + (" Your parent sees a live pin in Telegram." if parent_ok else " Connect Telegram in Step 0."))

def trigger_sos(reason):
    if not has_loc:
        st.error("Location is not available yet. Do Step 1 first.")
        return
    lat, lon = loc["latitude"], loc["longitude"]
    link = f"https://maps.google.com/?q={lat},{lon}"
    log_location()
    box["alerts"].append({"time": f"{datetime.now():%d %b %H:%M:%S}", "reason": reason, "link": link})
    if parent_ok:
        ok, msg = send_message("parent", f"🚨 EMERGENCY! Your child needs help ({reason}).\nMap: {link}")
        send_location("parent", lat, lon)
        st.error("SOS sent to your parent on Telegram.") if ok else st.warning(f"Alert saved but Telegram failed: {msg}")
    else:
        st.warning("Alert saved. Connect your parent's Telegram (Step 0) to send it.")

st.write("**Step 2.** In danger? Press the button.")
if st.button("🚨 SOS - I need help"):
    trigger_sos("SOS button")

st.write("**Or say the word 'help'** (record, then it is checked automatically):")
voice = st.audio_input("🎤 Say 'help'")
if voice and st.session_state.get("last_voice") != voice.size:
    st.session_state.last_voice = voice.size
    try:
        data = parse_json(ask_gemini('Listen to the audio. Reply ONLY with JSON {"help": true or false}. '
                                     'true if the person says help, save me, bachao or similar.',
                                     audio=voice.getvalue()))
        trigger_sos("voice: help") if data.get("help") else st.info("No emergency word heard.")
    except Exception as e:
        st.error(f"Could not check the audio: {e}")

st.divider()
st.write("**Messages from your parent** (they reply to the bot in Telegram)")
if parent_ok and st.button("Check messages"):
    msgs = replies("parent")
    for m in msgs:
        st.write("👨‍👩‍👧 " + m)
    if not msgs:
        st.info("No messages yet.")

st.caption("Limits: the page must be open with location allowed. Always-on listening in the background needs a mobile app (future scope).")
