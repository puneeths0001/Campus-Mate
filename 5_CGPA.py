# pages/5_CGPA.py - enter FINAL MARKS per subject; we convert them to grades, SGPA and improvement tips
import streamlit as st
import pandas as pd
from theme import apply_theme, glass_table

st.set_page_config(page_title="CGPA | Campus Mate", page_icon="📊", layout="wide")
apply_theme()
st.title("📊 SGPA / CGPA planner")
st.caption("VTU engineering · 10-point scale · SGPA = Σ(credits × grade points) ÷ Σ credits")

# VTU 10-point scale (2022 / 2025 scheme). Grade points are fixed; the marks needed for each grade can be edited below.
POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}
DEFAULT_FROM = {"O": 90, "A+": 80, "A": 70, "B+": 60, "B": 55, "C": 50, "P": 40}

with st.expander("VTU grade scale: marks → grade (2022 / 2025 scheme, editable)"):
    st.caption("These are the usual VTU cut-offs. If your scheme document shows different numbers, change them here.")
    cols = st.columns(4)
    scale = {"F": 0}
    for i, g in enumerate(DEFAULT_FROM):
        scale[g] = cols[i % 4].number_input(f"{g} from", min_value=0, max_value=100, value=DEFAULT_FROM[g], key=f"sc_{g}")

def grade_of(marks):
    for g in POINTS:                      # from the best grade down
        if marks >= scale[g]:
            return g
    return "F"

def next_grade(g):
    keys = list(POINTS)
    i = keys.index(g)
    return keys[i - 1] if i > 0 else None

if "subjects_m" not in st.session_state:
    first = [("Maths", 4, 68), ("Physics", 3, 82), ("Programming", 4, 75), ("English", 2, 85)]
    st.session_state.subjects_m = [{"id": i + 1, "Subject": n, "Credits": c, "Marks": m} for i, (n, c, m) in enumerate(first)]
    st.session_state.sid_m = len(first)

st.write("Enter your **final marks out of 100** for each subject. Press **＋ Add subject** for more.")
head = st.columns([4, 2, 2, 2, 1])
for col, label in zip(head, ["Subject", "Credits", "Final marks", "Grade"]):
    col.caption(label)
for s in list(st.session_state.subjects_m):
    c = st.columns([4, 2, 2, 2, 1], vertical_alignment="center")
    s["Subject"] = c[0].text_input("Subject", value=s["Subject"], key=f"m_sub_{s['id']}", label_visibility="collapsed")
    s["Credits"] = c[1].number_input("Credits", min_value=1, max_value=10, value=int(s["Credits"]),
                                     key=f"m_cr_{s['id']}", label_visibility="collapsed")
    s["Marks"] = c[2].number_input("Final marks", min_value=0, max_value=100, value=int(s["Marks"]),
                                   key=f"m_mk_{s['id']}", label_visibility="collapsed")
    g = grade_of(s["Marks"])
    c[3].markdown(f"**{g}** · {POINTS[g]} pts")          # the grade is worked out automatically
    if c[4].button("✕", key=f"m_rm_{s['id']}", help="Remove this subject"):
        st.session_state.subjects_m.remove(s)
        st.rerun()
if st.button("＋ Add subject"):
    st.session_state.sid_m += 1
    st.session_state.subjects_m.append({"id": st.session_state.sid_m, "Subject": "", "Credits": 3, "Marks": 60})
    st.rerun()

table = pd.DataFrame(st.session_state.subjects_m)
table = table[table["Subject"].str.strip() != ""] if not table.empty else table
if table.empty:
    st.info("Add at least one subject.")
    st.stop()

table["Grade"] = table["Marks"].map(grade_of)
table["Points"] = table["Grade"].map(POINTS)
total_credits = table["Credits"].sum()
sgpa = (table["Credits"] * table["Points"]).sum() / total_credits
avg_marks = (table["Credits"] * table["Marks"]).sum() / total_credits
# SGPA you lose = how far this subject keeps your SGPA below a perfect 10
table["Lose"] = table["Credits"] * (10 - table["Points"]) / total_credits

m1, m2 = st.columns(2)
m1.metric("Your SGPA", f"{sgpa:.2f}")
m2.metric("Average marks (weighted by credits)", f"{avg_marks:.1f}")

# How many more marks lift each subject to the next grade, and what that adds to the SGPA
tips = []
for _, r in table.iterrows():
    nxt = next_grade(r["Grade"])
    if nxt:
        need = max(0, scale[nxt] - r["Marks"])
        gain = r["Credits"] * (POINTS[nxt] - r["Points"]) / total_credits
        tips.append({"Subject": r["Subject"], "nxt": nxt, "need": need, "gain": gain})
tipmap = {t["Subject"]: t for t in tips}

st.subheader("Where to improve")
worst = table.sort_values("Lose", ascending=False)
show = pd.DataFrame({
    "Subject": worst["Subject"], "Credits": worst["Credits"], "Marks": worst["Marks"], "Grade": worst["Grade"],
    "SGPA you lose": worst["Lose"].map(lambda v: f"{v:.2f}"),
    "To reach next grade": [f"+{tipmap[x]['need']} marks for {tipmap[x]['nxt']}" if x in tipmap else "Top grade"
                            for x in worst["Subject"]],
})
glass_table(show, right=["Credits", "Marks", "SGPA you lose"])

top = worst.iloc[0]
if top["Lose"] > 0:
    st.success(f"Biggest loss: {top['Subject']} ({top['Credits']} credits) is costing you {top['Lose']:.2f} SGPA points.")
wins = [t for t in tips if t["need"] > 0]
if wins:
    best = max(wins, key=lambda t: t["gain"] / t["need"])
    st.info(f"Quickest win: {best['need']} more marks in {best['Subject']} lifts it to {best['nxt']} "
            f"and adds {best['gain']:.2f} to your SGPA.")

st.subheader("Your overall CGPA")
c1, c2 = st.columns(2)
old_cgpa = c1.number_input("CGPA before this semester", 0.0, 10.0, 7.5)
old_credits = c2.number_input("Credits completed before", 0, 300, 40)
cgpa = (old_cgpa * old_credits + sgpa * total_credits) / (old_credits + total_credits)
st.metric("New CGPA", f"{cgpa:.2f}")
