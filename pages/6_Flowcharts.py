# pages/6_Flowcharts.py - turns notes into a flowchart using Gemini
import streamlit as st
from theme import apply_theme
from ai import ask_gemini, strip_fences

st.set_page_config(page_title="Flowcharts | Campus Mate", page_icon="🧠", layout="wide")
apply_theme()
st.title("🧠 Notes to flowchart")

notes = st.text_area("Paste your notes", height=220,
                     placeholder="Photosynthesis: sunlight hits chlorophyll, water splits, ...")
direction = st.radio("Layout", ["Top to bottom", "Left to right"], horizontal=True)

if st.button("Make flowchart") and notes.strip():
    rank = "TB" if direction == "Top to bottom" else "LR"
    prompt = f"""Turn these study notes into a clear flowchart in Graphviz DOT language.
Rules: reply with DOT code only. Use digraph with rankdir={rank}. Keep node labels under 6 words.
Use shape=box, style="rounded,filled", fillcolor in soft pastel colors, fontname="Helvetica".
Use at most 15 nodes and group the main ideas.
NOTES:
{notes}"""
    try:
        with st.spinner("Gemini is drawing..."):
            dot = strip_fences(ask_gemini(prompt))
        st.graphviz_chart(dot, use_container_width=True)
        st.download_button("Download DOT file", dot, "flowchart.dot")
        with st.expander("See the code Gemini wrote"):
            st.code(dot)
    except Exception as e:
        st.error(f"Could not make the flowchart: {e}")
