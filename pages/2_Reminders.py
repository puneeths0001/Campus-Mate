# pages/2_Reminders.py - three side-by-side boards: announcements, assignments, exams
import streamlit as st
from datetime import datetime, date
from theme import apply_theme
from ai import ask_gemini, parse_json
from notify import link_widget, send_message

st.set_page_config(page_title="Reminder | Campus Mate", page_icon="⏰", layout="wide")
apply_theme()
st.title("⏰ Reminder")

if "reminders" not in st.session_state:
    st.session_state.reminders = []   # each item: id, Type, Task, Due (a date and time, or None)
    st.session_state.rid = 0

KINDS = {   # kind: (icon, title, example shown in the box)
    "announcement": ("📢", "Important announcements", "e.g. College closed this Friday"),
    "assignment": ("📝", "Assignment reminder", "e.g. Maths assignment due Friday 5 pm"),
    "exam": ("🎯", "Upcoming exams", "e.g. DBMS exam 24 Nov 10 am"),
}

def add_item(kind, words=None, audio=None):
    """Gemini reads the typed or spoken words and returns a short title plus the date and time (if any)."""
    prompt = f"""Today is {date.today()} ({date.today():%A}). A student saved a {kind}
{'in the audio' if audio else 'as text: ' + words}. Reply ONLY with JSON:
{{"task": "short title", "date": "YYYY-MM-DD or null", "time": "HH:MM or null"}}.
Use null for the date if none is mentioned. If a date is given without a time, use 09:00."""
    try:
        data = parse_json(ask_gemini(prompt, audio=audio.getvalue() if audio else None))
    except Exception:
        if audio:
            raise
        data = {"task": words, "date": None, "time": None}   # typed text is still saved without AI
    due = None
    if data.get("date"):
        try:
            due = datetime.strptime(f"{data['date']} {data.get('time') or '09:00'}", "%Y-%m-%d %H:%M")
        except ValueError:
            pass
    st.session_state.rid += 1
    st.session_state.reminders.append({"id": st.session_state.rid, "Type": kind, "Task": data["task"], "Due": due})
    st.toast(f"Added: {data['task']}")

def when(due):
    if due is None:
        return "📌 No date"
    hours = (due - datetime.now()).total_seconds() / 3600
    tag = "⚠️ Overdue" if hours < 0 else "🔔 Within 24 hours" if hours <= 24 else "✅ Upcoming"
    return f"{due:%d %b, %I:%M %p} · {tag}"

cols = st.columns(3)
for col, (kind, (icon, title, hint)) in zip(cols, KINDS.items()):
    with col, st.container(border=True):
        st.subheader(f"{icon} {title}")

        # 1) Type first
        with st.form(f"form_{kind}", clear_on_submit=True, border=False):
            typed = st.text_input("Type", placeholder=hint, label_visibility="collapsed")
            if st.form_submit_button("Add") and typed.strip():
                try:
                    add_item(kind, words=typed.strip())
                except Exception as e:
                    st.error(f"Could not add: {e}")

        # 2) Small voice recorder
        st.caption("🎤 or speak it")
        audio = st.audio_input("Speak", key=f"mic_{kind}", label_visibility="collapsed")
        if audio and st.session_state.get(f"seen_{kind}") != audio.size:
            st.session_state[f"seen_{kind}"] = audio.size
            try:
                add_item(kind, audio=audio)
            except Exception as e:
                st.error(f"Could not understand that: {e}")

        # 3) This board's list
        mine = [r for r in st.session_state.reminders if r["Type"] == kind]
        mine.sort(key=lambda r: (r["Due"] is None, r["Due"] or datetime.max))
        if not mine:
            st.caption("Nothing here yet.")
        for r in mine:
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{r['Task']}**")
            c1.caption(when(r["Due"]))
            if c2.button("✓", key=f"done_{r['id']}", help="Done"):
                st.session_state.reminders.remove(r)
                st.rerun()

# Send everything due in the next 24 hours to the student's own Telegram
soon = [r for r in st.session_state.reminders
        if r["Due"] and 0 <= (r["Due"] - datetime.now()).total_seconds() <= 86400]
if soon:
    st.warning(f"{len(soon)} item(s) due in the next 24 hours.")
    if link_widget("student", "You"):
        if st.button("Send these to my Telegram"):
            ok, msg = send_message("student", "Campus Mate reminders:\n" + "\n".join(
                f"- {r['Task']} ({r['Due']:%d %b %I:%M %p})" for r in soon))
            st.write("Sent" if ok else msg)
st.caption("Items are kept while the page is open. Alerts when the app is closed need a background server (future scope).")
