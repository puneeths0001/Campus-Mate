# notify.py - sends SMS or WhatsApp messages through Twilio
import requests
import streamlit as st

def send_sms(to, body, whatsapp=False):
    """Returns (True/False, message). Keys come from secrets.toml."""
    try:
        sid, token, sender = st.secrets["TWILIO_SID"], st.secrets["TWILIO_TOKEN"], st.secrets["TWILIO_FROM"]
    except Exception:
        return False, "Twilio keys are missing in .streamlit/secrets.toml"
    if whatsapp:   # WhatsApp numbers are written as whatsapp:+91...
        to, sender = f"whatsapp:{to}", f"whatsapp:{sender}"
    r = requests.post(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                      auth=(sid, token), data={"To": to, "From": sender, "Body": body}, timeout=30)
    return (r.status_code in (200, 201)), ("Sent" if r.status_code in (200, 201) else r.text[:200])
