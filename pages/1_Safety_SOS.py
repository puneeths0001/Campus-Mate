# pages/1_Safety_SOS.py - SOS alert, live location, and a parent view
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_geolocation import streamlit_geolocation
from streamlit_autorefresh import st_autorefresh
from theme import apply_theme
from ai import ask_gemini, parse_json
from notify import send_sms

st.set_page_config(page_title="Safety | Campus Mate", page_icon="🚨", layout="wide")
apply_theme()

@st.cache_resource
def shared():
    """One dictionary shared by every visitor while the server runs. This is how the parent sees the student."""
    return {"locations": [], "alerts": []}
box = shared()

# ---------- Parent view: open this page with ?parent=1 at the end of the link ----------
if st.query_params.get("parent"):
    st_autorefresh(interval=30000, key="parent_refresh")   # refresh every 30 seconds
    st.title("👨‍👩‍👧 Parent view")
    if box["alerts"]:
        a = box["alerts"][-1]
        st.error(f"🚨 EMERGENCY at {a['time']} ({a['reason']}). Map: {a['link']}")
    if box["locations"]:
        df = pd.DataFrame(box["locations"])
        last = df.iloc[-1]
        st.metric("Last seen", last["time"])
        st.map(df[["lat", "lon"]])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("The student has not shared location yet.")
    st.stop()

# ---------- Student view ----------
st.title("🚨 Safety")
c1, c2 = st.columns(2)
parent = c1.text_input("Parent's phone (+91...)")
wa = c2.checkbox("Send on WhatsApp (Twilio sandbox)")

st.write("**Step 1.** Tap the target button and allow location in your browser.")
loc = streamlit_geolocation()
has_loc = bool(loc and loc.get("latitude"))

def log_location():
    box["locations"].append({"time": f"{datetime.now():%d %b %H:%M:%S}",
                             "lat": loc["latitude"], "lon": loc["longitude"]})

share = st.toggle("Share my live location with my parents (updates every 5 minutes)")
if share and has_loc:
    st_autorefresh(interval=300000, key="share_refresh")   # re-runs this page every 5 minutes
    # save a point only if the last one is older than 4 minutes (avoids duplicates on every re-run)
    if (datetime.now() - box.get("last_log", datetime.min)).total_seconds() > 240:
        log_location()
        box["last_log"] = datetime.now()
    st.success("Sharing is on. Parents can open this page with ?parent=1 added to the link.")

def trigger_sos(reason):
    if not has_loc:
        st.error("Location is not available yet. Do Step 1 first.")
        return
    link = f"https://maps.google.com/?q={loc['latitude']},{loc['longitude']}"
    log_location()
    box["alerts"].append({"time": f"{datetime.now():%d %b %H:%M:%S}", "reason": reason, "link": link})
    if parent:
        ok, msg = send_sms(parent, f"EMERGENCY from Campus Mate: I need help. My live location: {link}", whatsapp=wa)
        st.error(f"SOS sent to your parent: {msg}") if ok else st.warning(f"Alert saved but message not sent: {msg}")
    else:
        st.warning("Alert saved. Add your parent's phone number to send a message.")

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

st.caption("Limits: the page must be open with location allowed. Always-on listening in the background needs a mobile app (future scope).")
