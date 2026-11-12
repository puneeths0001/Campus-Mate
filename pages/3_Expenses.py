# pages/3_Expenses.py - Expense tracker with a monthly limit warning
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from theme import apply_theme, glass_table

st.set_page_config(page_title="Expenses | Campus Mate", page_icon="💸", layout="wide")
apply_theme()
head, side = st.columns([3, 1], vertical_alignment="bottom")
head.title("💸 Expense tracker")
limit = side.number_input("Monthly limit (₹)", min_value=0, value=5000, step=500)

# session_state remembers data while the page is open (it resets on refresh)
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Amount", "Category", "Payment method"])


with st.form("add_expense", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    d = c1.date_input("Date", date.today(), format="DD/MM/YYYY")
    amt = c2.number_input("Amount (₹)", min_value=0.0, step=10.0)
    cat = c3.selectbox("Spent on", ["Food", "Travel", "Books", "Recharge", "Rent", "Other"],
                       accept_new_options=True, placeholder="Pick or type your own")   # typing a new word is allowed
    pay = c4.selectbox("Paid by", ["UPI", "Cash", "Card"])
    if st.form_submit_button("Add expense") and amt > 0:
        new = pd.DataFrame([[pd.Timestamp(d), amt, cat, pay]],
                           columns=st.session_state.expenses.columns)
        st.session_state.expenses = pd.concat([st.session_state.expenses, new], ignore_index=True)

df = st.session_state.expenses
if df.empty:
    st.info("No expenses yet. Add your first one above.")
else:
    this_month = df[pd.to_datetime(df["Date"]).dt.month == date.today().month]
    spent = float(this_month["Amount"].sum())
    left = limit - spent
    m1, m2, m3 = st.columns(3)
    m1.metric("Spent this month", f"₹{spent:,.0f}")
    m2.metric("Limit", f"₹{limit:,.0f}")
    m3.metric("Left", f"₹{left:,.0f}")
    st.progress(min(spent / limit, 1.0) if limit else 1.0)
    if limit and spent > limit:
        st.error(f"Limit crossed by ₹{spent - limit:,.0f}. Cut spending for the rest of the month.")
    elif limit and spent > 0.8 * limit:
        st.warning("You have used more than 80% of your monthly limit.")

    a, b = st.columns(2)
    def glassfig(fig):   # dark, see-through charts with white text, whatever the viewer's device theme is
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#fff", margin=dict(t=50, l=10, r=10, b=10))
        return fig
    a.plotly_chart(glassfig(px.pie(df, values="Amount", names="Category", hole=0.45,
                                   title="Where the money went")), use_container_width=True, theme=None)
    b.plotly_chart(glassfig(px.bar(df.groupby("Payment method", as_index=False)["Amount"].sum(),
                                   x="Payment method", y="Amount", title="By payment method")),
                   use_container_width=True, theme=None)
    st.subheader("All expenses")
    show = df.copy()
    show["Date"] = pd.to_datetime(show["Date"]).dt.strftime("%d/%m/%Y")
    show["Amount"] = show["Amount"].map(lambda v: f"₹{v:,.2f}")
    glass_table(show.iloc[::-1], right=["Amount"])   # newest first
