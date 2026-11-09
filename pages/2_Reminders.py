# pages/2_Reminders.py - three side-by-side boards: announcements, assignments, exams
import streamlit as st
from datetime import datetime, date, time as dtime
from theme import apply_theme
from ai import ask_gemini, parse_json
from notify import link_widget, send_message
from when_parse import parse_date, parse_time, fmt

st.set_page_config(page_title="Reminder | Campus Mate", page_icon="⏰", layout="wide")
apply_theme()
st.title("⏰ Reminder")

if "reminders" not in st.session_state:
    st.session_state.reminders = []   # each item: id, Type, Task, Due (date and time or None), HasTime
    st.session_state.rid = 0

KINDS = {   # kind: (icon, title, example shown in the box)
    "announcement": ("📢", "Important announcements", "e.g. College closed this Friday"),
    "assignment": ("📝", "Assignment reminder", "e.g. Maths assignment submission"),
    "exam": ("🎯", "Upcoming exams", "e.g. DBMS exam"),
}

def add_item(kind, task, due, has_time):
    st.session_state.rid += 1
    st.session_state.reminders.append({"id": st.session_state.rid, "Type": kind, "Task": task, "Due": due, "HasTime": has_time})

def add_cb(kind):
    """Runs when you press Add. Reads the boxes, checks them, saves the item and empties the boxes."""
    ss = st.session_state
    task = ss.get(f"task_{kind}", "").strip()
    if not task:
        return
    dtxt, ttxt = ss.get(f"date_{kind}", "").strip(), ss.get(f"time_{kind}", "").strip()
    d = parse_date(dtxt) if dtxt else None
    t = parse_time(ttxt, ss.get(f"ampm_{kind}", "AM")) if ttxt else None
    if (dtxt and d is None) or (ttxt and t is None):
        ss[f"err_{kind}"] = "Check the date (like 25/11) and the time (like 5:30)."
        return
    # a date with no time means "by the end of that day"
    due = datetime.combine(d, t or dtime(23, 59)) if d else None
    add_item(kind, task, due, bool(d and t))
    for box in ("task", "date", "time", "err"):
        ss[f"{box}_{kind}"] = ""

def done_cb(rid):
    st.session_state.reminders = [r for r in st.session_state.reminders if r["id"] != rid]

def add_from_voice(kind, audio):
    """Only spoken reminders use AI: Gemini listens and returns a title, date and time."""
    prompt = f"""Today is {date.today()} ({date.today():%A}). A student spoke a {kind} reminder in the audio.
Reply ONLY with JSON: {{"task": "short title", "date": "YYYY-MM-DD or null", "time": "HH:MM in 24-hour or null"}}.
Use null for the date if none is said, and null for the time if no time is said."""
    data = parse_json(ask_gemini(prompt, audio=audio.getvalue()))
    due, has_time = None, False
    if data.get("date"):
        try:
            due = datetime.strptime(f"{data['date']} {data.get('time') or '23:59'}", "%Y-%m-%d %H:%M")
            has_time = bool(data.get("time"))
        except ValueError:
            pass
    add_item(kind, data["task"], due, has_time)

def when(r):
    due = r["Due"]
    if due is None:
        return "📌 No date"
    hours = (due - datetime.now()).total_seconds() / 3600
    tag = "⚠️ Overdue" if hours < 0 else "🔔 Within 24 hours" if hours <= 24 else "✅ Upcoming"
    return f"{fmt(due, r.get('HasTime', True))} · {tag}"

def board(kind):
    icon, title, hint = KINDS[kind]
    with st.container(border=True):
        st.subheader(f"{icon} {title}")

        # 1) Type first. Date and time are typed too, and both are optional.
        st.text_input("Type", placeholder=hint, key=f"task_{kind}", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        date_txt = c1.text_input("Date", placeholder="Date, e.g. 25/11", key=f"date_{kind}", label_visibility="collapsed")
        c2.text_input("Time", placeholder="Time, e.g. 5:30", key=f"time_{kind}", label_visibility="collapsed")
        st.radio("AM or PM", ["AM", "PM"], horizontal=True, key=f"ampm_{kind}", label_visibility="collapsed")
        if date_txt.strip():                         # the weekday is worked out for you
            d = parse_date(date_txt)
            st.caption(f"📅 {d:%A, %d %B %Y}" if d else "Type the date like 25/11 or 25/11/2026")
        if st.session_state.get(f"err_{kind}"):
            st.error(st.session_state[f"err_{kind}"])
        st.button("Add", key=f"add_{kind}", on_click=add_cb, args=(kind,))

        # 2) Small voice recorder (this one uses AI to find the date and time in what you say)
        st.caption("🎤 or speak it")
        audio = st.audio_input("Speak", key=f"mic_{kind}", label_visibility="collapsed")
        if audio and st.session_state.get(f"seen_{kind}") != audio.size:
            st.session_state[f"seen_{kind}"] = audio.size
            try:
                with st.spinner("Listening..."):
                    add_from_voice(kind, audio)
            except Exception as e:
                st.error(f"Could not understand that: {e}")

        # 3) This board's list
        mine = [r for r in st.session_state.reminders if r["Type"] == kind]
        mine.sort(key=lambda r: (r["Due"] is None, r["Due"] or datetime.max))
        if not mine:
            st.caption("Nothing here yet.")
        for r in mine:
            a, b = st.columns([5, 1])
            a.markdown(f"**{r['Task']}**")
            a.caption(when(r))
            b.button("✓", key=f"done_{r['id']}", help="Done", on_click=done_cb, args=(r["id"],))

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
                f"- {r['Task']} ({fmt(r['Due'], r.get('HasTime', True))})" for r in soon))
            st.write("Sent" if ok else msg)
st.caption("Items are kept while the page is open. Alerts when the app is closed need a background server (future scope).")
