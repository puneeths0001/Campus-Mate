# pages/5_CGPA.py - SGPA calculator with improvement hints (glass input rows and glass table)
import streamlit as st
import pandas as pd
from theme import apply_theme, glass_table

st.set_page_config(page_title="CGPA | Campus Mate", page_icon="📊", layout="wide")
apply_theme()
st.title("📊 SGPA / CGPA planner")

# Common 10-point scale. Change these numbers if your university is different.
POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "F": 0}
GRADES = list(POINTS)

if "subjects" not in st.session_state:
    first = [("Maths", 4, "B"), ("Physics", 3, "A"), ("Programming", 4, "B+"), ("English", 2, "A")]
    st.session_state.subjects = [{"id": i + 1, "Subject": n, "Credits": c, "Grade": g} for i, (n, c, g) in enumerate(first)]
    st.session_state.sid = len(first)

st.write("Fill in your subjects, credits and grades. Press **＋ Add subject** for more.")
head = st.columns([4, 2, 2, 1])
head[0].caption("Subject"); head[1].caption("Credits"); head[2].caption("Grade")
for s in list(st.session_state.subjects):
    c = st.columns([4, 2, 2, 1])
    s["Subject"] = c[0].text_input("Subject", value=s["Subject"], key=f"sub_{s['id']}", label_visibility="collapsed")
    s["Credits"] = c[1].number_input("Credits", min_value=1, max_value=10, value=int(s["Credits"]),
                                     key=f"cr_{s['id']}", label_visibility="collapsed")
    s["Grade"] = c[2].selectbox("Grade", GRADES, index=GRADES.index(s["Grade"]),
                                key=f"gr_{s['id']}", label_visibility="collapsed")
    if c[3].button("✕", key=f"rm_{s['id']}", help="Remove this subject"):
        st.session_state.subjects.remove(s)
        st.rerun()
if st.button("＋ Add subject"):
    st.session_state.sid += 1
    st.session_state.subjects.append({"id": st.session_state.sid, "Subject": "", "Credits": 3, "Grade": "B"})
    st.rerun()

table = pd.DataFrame(st.session_state.subjects)
table = table[table["Subject"].str.strip() != ""] if not table.empty else table
if table.empty:
    st.info("Add at least one subject.")
    st.stop()

table["Points"] = table["Grade"].map(POINTS)
total_credits = table["Credits"].sum()
sgpa = (table["Credits"] * table["Points"]).sum() / total_credits
# Marks lost = how much this subject keeps your SGPA below a perfect 10
table["SGPA you lose"] = (table["Credits"] * (10 - table["Points"]) / total_credits)

st.metric("Your SGPA", f"{sgpa:.2f}")
worst = table.sort_values("SGPA you lose", ascending=False)
st.subheader("Where to improve")
show = worst[["Subject", "Credits", "Grade", "SGPA you lose"]].copy()
show["SGPA you lose"] = show["SGPA you lose"].map(lambda v: f"{v:.2f}")
glass_table(show, right=["Credits", "SGPA you lose"])
top = worst.iloc[0]
if top["SGPA you lose"] > 0:
    st.success(f"Focus on {top['Subject']} first. It has {top['Credits']} credits and "
               f"is costing you {top['SGPA you lose']:.2f} SGPA points.")

st.subheader("Your overall CGPA")
c1, c2 = st.columns(2)
old_cgpa = c1.number_input("CGPA before this semester", 0.0, 10.0, 7.5)
old_credits = c2.number_input("Credits completed before", 0, 300, 40)
cgpa = (old_cgpa * old_credits + sgpa * total_credits) / (old_credits + total_credits)
st.metric("New CGPA", f"{cgpa:.2f}")
