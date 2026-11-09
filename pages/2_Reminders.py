# pages/2_Reminders.py - three side-by-side boards: announcements, assignments, exams
import streamlit as st
from datetime import datetime, date, time as dtime
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
    "assignment": ("📝", "Assignment reminder", "e.g. Maths assignment submission"),
    "exam": ("🎯", "Upcoming exams", "e.g. DBMS exam"),
}

def add_item(kind, task, due):
    st.session_state.rid += 1
    st.session_state.reminders.append({"id": st.session_state.rid, "Type": kind, "Task": task, "Due": due})

def add_from_voice(kind, audio):
    """Only the spoken reminders use AI: Gemini listens and returns a title, date and time."""
    prompt = f"""Today is {date.today()} ({date.today():%A}). A student spoke a {kind} reminder in the audio.
Reply ONLY with JSON: {{"task": "short title", "date": "YYYY-MM-DD or null", "time": "HH:MM or null"}}.
Use null for the date if none is said. If a date is given without a time, use 09:00."""
    data = parse_json(ask_gemini(prompt, audio=audio.getvalue()))
    due = None
    if data.get("date"):
        try:
            due = datetime.strptime(f"{data['date']} {data.get('time') or '09:00'}", "%Y-%m-%d %H:%M")
        except ValueError:
            pass
    add_item(kind, data["task"], due)

def when(due):
    if due is None:
        return "📌 No date"
    hours = (due - datetime.now()).total_seconds() / 3600
    tag = "⚠️ Overdue" if hours < 0 else "🔔 Within 24 hours" if hours <= 24 else "✅ Upcoming"
    return f"{due:%d/%m/%Y, %I:%M %p} · {tag}"

@st.fragment   # each board refreshes by itself, so the other boards do not grey out while it works
def board(kind):
    icon, title, hint = KINDS[kind]
    with st.container(border=True):
        st.subheader(f"{icon} {title}")

        # 1) Type first, with an optional date and time you pick yourself (instant, no AI needed)
        added = False
        with st.form(f"form_{kind}", clear_on_submit=True, border=False):
            typed = st.text_input("Type", placeholder=hint, label_visibility="collapsed")
            c1, c2 = st.columns(2)
            d = c1.date_input("Date", value=None, format="DD/MM/YYYY", label_visibility="collapsed",
                              placeholder="Date (optional)")
            t = c2.time_input("Time", value=dtime(9, 0), label_visibility="collapsed")
            if st.form_submit_button("Add") and typed.strip():
                add_item(kind, typed.strip(), datetime.combine(d, t) if d else None)
                added = True
        if added:
            st.rerun()

        # 2) Small voice recorder (this one uses AI to find the date and time in what you say)
        st.caption("🎤 or speak it")
        audio = st.audio_input("Speak", key=f"mic_{kind}", label_visibility="collapsed")
        heard = False
        if audio and st.session_state.get(f"seen_{kind}") != audio.size:
            st.session_state[f"seen_{kind}"] = audio.size
            try:
                with st.spinner("Listening..."):
                    add_from_voice(kind, audio)
                heard = True
            except Exception as e:
                st.error(f"Could not understand that: {e}")
        if heard:
            st.rerun()

        # 3) This board's list
        mine = [r for r in st.session_state.reminders if r["Type"] == kind]
        mine.sort(key=lambda r: (r["Due"] is None, r["Due"] or datetime.max))
        if not mine:
            st.caption("Nothing here yet.")
        done = None
        for r in mine:
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{r['Task']}**")
            c1.caption(when(r["Due"]))
            if c2.button("✓", key=f"done_{r['id']}", help="Done"):
                done = r
        if done:
            st.session_state.reminders.remove(done)
            st.rerun()

cols = st.columns(3)
for col, kind in zip(cols, KINDS):
    with col:
        board(kind)

# Send everything due in the next 24 hours to the student's own Telegram
soon = [r for r in st.session_state.reminders
        if r["Due"] and 0 <= (r["Due"] - datetime.now()).total_seconds() <= 86400]
if soon:
    st.warning(f"{len(soon)} item(s) due in the next 24 hours.")
    if link_widget("student", "You"):
        if st.button("Send these to my Telegram"):
            ok, msg = send_message("student", "Campus Mate reminders:\n" + "\n".join(
                f"- {r['Task']} ({r['Due']:%d/%m/%Y %I:%M %p})" for r in soon))
            st.write("Sent" if ok else msg)
st.caption("Items are kept while the page is open. Alerts when the app is closed need a background server (future scope).")
