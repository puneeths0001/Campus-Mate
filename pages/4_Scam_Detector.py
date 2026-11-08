# pages/4_Scam_Detector.py - paste a link, email or offer and get a risk score
import streamlit as st
from theme import apply_theme
from scam_rules import analyze

st.set_page_config(page_title="Scam Detector | Campus Mate", page_icon="🛡️", layout="wide")
apply_theme()
st.title("🛡️ Scam detector")
st.write("Paste a link, an email or an internship or scholarship offer.")

text = st.text_area("Paste here", height=200,
                    placeholder="Congratulations! You are selected. Pay a registration fee at http://...")
if st.button("Check now") and text.strip():
    score, level, reasons = analyze(text)
    c1, c2 = st.columns(2)
    c1.metric("Risk score", f"{score} / 100")
    c2.metric("Verdict", level)
    st.progress(score / 100)
    if score >= 55:
        st.error("Do not click, reply or pay. Show it to a teacher or your college placement cell.")
    elif score >= 25:
        st.warning("Be careful. Check the sender on the official website before doing anything.")
    else:
        st.success("No strong warning signs found. This is not a guarantee, so stay alert.")
    if reasons:
        st.subheader("Why")
        for r in reasons:
            st.write("• " + r)
st.caption("This tool checks warning signs with rules. It cannot prove a link is safe.")
