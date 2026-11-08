# pages/5_CGPA.py - SGPA calculator with improvement hints
import streamlit as st
import pandas as pd
from theme import apply_theme

st.set_page_config(page_title="CGPA | Campus Mate", page_icon="📊", layout="wide")
apply_theme()
st.title("📊 SGPA / CGPA planner")

# Common 10-point scale. Change these numbers if your university is different.
POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "F": 0}

st.write("Edit the table. Add rows with the + at the bottom.")
start = pd.DataFrame({"Subject": ["Maths", "Physics", "Programming", "English"],
                      "Credits": [4, 3, 4, 2],
                      "Grade": ["B", "A", "B+", "A"]})
table = st.data_editor(start, num_rows="dynamic", use_container_width=True,
                       column_config={"Grade": st.column_config.SelectboxColumn(options=list(POINTS))})

table = table.dropna()
if table.empty:
    st.info("Add at least one subject.")
    st.stop()

table["Points"] = table["Grade"].map(POINTS)
total_credits = table["Credits"].sum()
sgpa = (table["Credits"] * table["Points"]).sum() / total_credits
# Marks lost = how much this subject keeps your SGPA below a perfect 10
table["SGPA you lose"] = (table["Credits"] * (10 - table["Points"]) / total_credits).round(2)

st.metric("Your SGPA", f"{sgpa:.2f}")
worst = table.sort_values("SGPA you lose", ascending=False)
st.subheader("Where to improve")
st.dataframe(worst[["Subject", "Credits", "Grade", "SGPA you lose"]], use_container_width=True)
top = worst.iloc[0]
if top["SGPA you lose"] > 0:
    st.success(f"Focus on {top['Subject']} first. It has {top['Credits']} credits and "
               f"is costing you {top['SGPA you lose']} SGPA points.")

st.subheader("Your overall CGPA")
c1, c2 = st.columns(2)
old_cgpa = c1.number_input("CGPA before this semester", 0.0, 10.0, 7.5)
old_credits = c2.number_input("Credits completed before", 0, 300, 40)
cgpa = (old_cgpa * old_credits + sgpa * total_credits) / (old_credits + total_credits)
st.metric("New CGPA", f"{cgpa:.2f}")
