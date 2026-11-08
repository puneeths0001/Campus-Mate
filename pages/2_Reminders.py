# pages/2_Reminders.py - speak or type a deadline, we keep it and warn you before it is due
import streamlit as st
import pandas as pd
from datetime import datetime, date
from theme import apply_theme
from ai import ask_gemini, parse_json
from notify import link_widget, send_message

st.set_page_config(page_title="Reminders | Campus Mate", page_icon="⏰", layout="wide")
apply_theme()
st.title("⏰ Voice reminders")

if "reminders" not in st.session_state:
    st.session_state.reminders = []   # list of {"Task":..., "Due": datetime}

def add_from_words(words=None, audio=None):
    prompt = f"""Today is {date.today()} ({date.today():%A}). The student gives a reminder
{'in the audio' if audio else 'as text: ' + words}. Reply ONLY with JSON:
{{"task": "short title", "date": "YYYY-MM-DD", "time": "HH:MM"}}. If no time is said, use 09:00."""
    data = parse_json(ask_gemini(prompt, audio=audio.getvalue() if audio else None))
    due = datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M")
    st.session_state.reminders.append({"Task": data["task"], "Due": due})
    st.success(f"Added: {data['task']} on {due:%d %b %Y, %I:%M %p}")

a, b = st.columns(2)
audio = a.audio_input("🎤 Say it, e.g. 'Maths assignment due Friday 5 pm'")
typed = b.text_input("Or type it")
try:
    if audio and st.session_state.get("last_audio") != audio.size:
        st.session_state.last_audio = audio.size
        add_from_words(audio=audio)
    if st.button("Add reminder") and typed:
        add_from_words(words=typed)
except Exception as e:
    st.error(f"Could not understand that: {e}")

items = sorted(st.session_state.reminders, key=lambda r: r["Due"])
if not items:
    st.info("No reminders yet.")
now = datetime.now()
soon = []
for i, r in enumerate(items):
    left = r["Due"] - now
    hours = left.total_seconds() / 3600
    status = "⚠️ Overdue" if hours < 0 else "🔔 Due within 24 hours" if hours <= 24 else "✅ Upcoming"
    if 0 <= hours <= 24: soon.append(r)
    c1, c2, c3 = st.columns([4, 3, 1])
    c1.write(f"**{r['Task']}**")
    c2.write(f"{r['Due']:%d %b, %I:%M %p}  ·  {status}")
    if c3.button("Done", key=f"del{i}"):
        st.session_state.reminders.remove(r)
        st.rerun()

if soon:
    st.warning(f"{len(soon)} reminder(s) due in the next 24 hours.")
    if link_widget("student", "You"):
        if st.button("Send these to my Telegram"):
            ok, msg = send_message("student", "Campus Mate reminders:\n" + "\n".join(
                f"- {r['Task']} ({r['Due']:%d %b %I:%M %p})" for r in soon))
            st.write("Sent" if ok else msg)
st.caption("Reminders are kept while the page is open. Alerts when the app is closed need a background server (future scope).")
