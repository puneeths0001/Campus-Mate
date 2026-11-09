# pages/6_Study_Buddy.py - a chat AI for doubts, step-by-step solutions, notes, flowcharts and quizzes
import re
import streamlit as st
from theme import apply_theme
from ai import chat_gemini

st.set_page_config(page_title="Study Buddy | Campus Mate", page_icon="🧠", layout="wide")
apply_theme()

SYSTEM = """You are Study Buddy, the AI tutor inside Campus Mate, for Indian engineering students (VTU).
Be friendly, clear and accurate. Explain simply first and go deeper when asked.
For problems, solve step by step and show the formulas. Write maths in LaTeX with $...$ or $$...$$.
For notes, use short headings and bullet points that are easy to revise before an exam.
For a flowchart, reply with Graphviz DOT inside a ```dot code block (at most 15 nodes) followed by one short sentence.
Start every DOT graph with exactly: digraph G { graph [bgcolor="transparent", rankdir=TB]; node [shape=box, style="rounded,filled", fillcolor="#CFC2FF", color="#7C5CFF", fontcolor="#0B0B0F", fontname="Helvetica"]; edge [color="#9A9AA5", fontcolor="#E8E8F0"];
Use rankdir=LR if the student asks for left to right.
If you are not sure about something, say so instead of guessing. Keep answers focused."""

MODES = {   # what each button adds in front of the student's message
    "💬 Ask / Solve": "",
    "📝 Make notes": "Make short, exam-ready notes on this: ",
    "🔀 Flowchart": "Make a flowchart (Graphviz DOT) for this: ",
    "❓ Quiz me": "Quiz me on this with 5 questions, one at a time. Wait for my answer before the next question: ",
}

if "chat" not in st.session_state:
    st.session_state.chat = []     # each message: role, text (shown), sent (what Gemini gets), imgs

def show(text):
    """Shows an answer. Flowchart code blocks are drawn as real diagrams."""
    parts = re.split(r"```(?:dot|graphviz)\s*\n(.*?)```", text, flags=re.S)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                st.markdown(part)
        else:
            st.graphviz_chart(part.strip(), use_container_width=True)
            with st.expander("See the flowchart code"):
                st.code(part.strip())

head, side = st.columns([4, 1], vertical_alignment="bottom")
head.title("🧠 Study Buddy")
if side.button("🗑 New chat"):
    st.session_state.chat = []
    st.rerun()

mode = st.radio("What do you want to do?", list(MODES), horizontal=True)

if not st.session_state.chat:
    st.caption("Ask a doubt, paste a question, attach a photo of a problem, or pick a mode above and paste your notes.")

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        for data, _ in m.get("imgs", []):
            st.image(data, width=260)
        show(m["text"]) if m["role"] == "assistant" else st.markdown(m["text"])

prompt = st.chat_input("Ask anything, or paste your notes...", accept_file=True,
                       file_type=["png", "jpg", "jpeg", "webp"])
if prompt:
    text = (prompt.text or "").strip()
    imgs = [(f.getvalue(), f.type or "image/png") for f in (prompt.files or [])]
    if not text and imgs:
        text = "Please solve or explain what is in this photo."
    if text:
        st.session_state.chat.append({"role": "user", "text": text, "sent": MODES[mode] + text, "imgs": imgs})
        with st.chat_message("user"):
            for data, _ in imgs:
                st.image(data, width=260)
            st.markdown(text)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    reply = chat_gemini(st.session_state.chat, SYSTEM)
                show(reply)
                st.session_state.chat.append({"role": "assistant", "text": reply, "sent": reply})
            except Exception as e:
                st.session_state.chat.pop()          # forget the failed question so you can simply send it again
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    st.error("Gemini is very busy right now. Wait a few seconds and send your message again.")
                else:
                    st.error(f"Could not get an answer: {e}")
