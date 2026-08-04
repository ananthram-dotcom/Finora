import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
from services.sheets_service import read_transactions

st.set_page_config(page_title="Aggregate Analytics", layout="wide")

if st.session_state.get("mode") != "Government":
    st.error("Access restricted to Government mode.")
    st.stop()

st.title("Aggregate Financial Analytics – Panchayat View")
st.caption("All 100 houses combined")

df = read_transactions()

if df.empty:
    st.info("No transactions in the sheet yet.")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Amount"])

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"₹{df[df['Type']=='Income']['Amount'].sum():,.0f}")
col2.metric("Total Expense", f"₹{df[df['Type']=='Expense']['Amount'].sum():,.0f}")
col3.metric("Net Balance", f"₹{(df[df['Type']=='Income']['Amount'].sum() - df[df['Type']=='Expense']['Amount'].sum()):,.0f}")
col4.metric("Active Houses", df["House_No"].nunique())

st.divider()

expense = df[df["Type"] == "Expense"]

# 1. Monthly trend
st.subheader("Monthly Income vs Expense")
monthly = df.groupby([df["Date"].dt.to_period("M"), "Type"])["Amount"].sum().reset_index()
monthly["Date"] = monthly["Date"].dt.to_timestamp()
fig1 = px.bar(monthly, x="Date", y="Amount", color="Type", barmode="group")
st.plotly_chart(fig1, use_container_width=True)

# 2. Category pie
st.subheader("Expense by Category")
cat_sum = expense.groupby("Category")["Amount"].sum().reset_index()
fig2 = px.pie(cat_sum, values="Amount", names="Category", hole=0.4)
st.plotly_chart(fig2, use_container_width=True)

# 3. Heatmap house vs category
st.subheader("Expenses: House vs Category")
pivot = expense.pivot_table(values="Amount", index="House_No", columns="Category", aggfunc="sum", fill_value=0)
fig3 = px.imshow(pivot, color_continuous_scale="RdBu_r", aspect="auto")
st.plotly_chart(fig3, use_container_width=True)

st.caption("If you still see 'Page not found' → double-check filename is **exactly** `Aggregate_Analytics.py` inside `pages/` folder")