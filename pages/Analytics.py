import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
from services.sheets_service import read_transactions
from services.ai_service import generate_insights

st.set_page_config(page_title="My Analytics", layout="wide")

# Guard
if "house_no" not in st.session_state or not st.session_state.house_no:
    st.error("Please select your House Number from the home page first.")
    st.stop()

house = st.session_state.house_no
st.markdown(f"## Financial Analytics – House {house}")
st.caption("Personal overview of income, expenses and balance")

# ────────────────────────────────────────────────
# Data loading – robust & forced datetime
# ────────────────────────────────────────────────
@st.cache_data(ttl=10, show_spinner="Loading your transactions…")
def get_my_transactions(house_number):
    df_all = read_transactions()
    df_house = df_all[df_all["House_No"] == house_number].copy()
    
    if df_house.empty:
        return df_house
    
    # Force numeric
    df_house["Amount"] = pd.to_numeric(df_house["Amount"], errors='coerce')
    
    # Date handling – try everything
    df_house["Date_raw"] = df_house["Date"].astype(str).str.strip()
    
    # First attempt: direct parse (ISO, YYYY-MM-DD, etc.)
    df_house["Date"] = pd.to_datetime(df_house["Date_raw"], errors='coerce')
    
    # Second attempt: if many NaT → treat as Excel serial number
    na_ratio = df_house["Date"].isna().mean()
    if na_ratio > 0.3:  # more than 30% failed
        temp = pd.to_numeric(df_house["Date_raw"], errors='coerce')
        mask = temp.notna()
        df_house.loc[mask, "Date"] = pd.to_datetime(
            temp[mask],
            unit='D',
            origin='1899-12-30',
            errors='coerce'
        )
    
    # Final cleanup
    df_house = df_house.dropna(subset=["Date", "Amount"])
    
    return df_house


# Refresh button
if st.button("↻ Refresh Data", type="primary"):
    st.cache_data.clear()
    st.rerun()

df = get_my_transactions(house)

income  = df[df["Type"] == "Income"]["Amount"].sum()  if not df.empty else 0.0
expense = df[df["Type"] == "Expense"]["Amount"].sum() if not df.empty else 0.0
balance = income - expense

k1, k2, k3 = st.columns(3)
k1.metric("Total Income",  f"₹{income:,.0f}")
k2.metric("Total Expense", f"₹{expense:,.0f}")
k3.metric("Net Balance",   f"₹{balance:,.0f}",
          delta=f"{balance:+,.0f}" if balance != 0 else None)

st.divider()

# ────────────────────────────────────────────────
# Monthly trend – SAFE version
# ────────────────────────────────────────────────
st.subheader("Monthly Income vs Expense Trend")

if df.empty:
    st.info("No transactions recorded for this house yet.")
else:
    # We already forced datetime in loading → should be datetime64[ns]
    # But add one final check
    if pd.api.types.is_datetime64_any_dtype(df["Date"]):
        try:
            monthly = (
                df.groupby([df["Date"].dt.to_period("M"), "Type"])["Amount"]
                  .sum()
                  .unstack(fill_value=0)
                  .reset_index()
            )
            monthly["Date"] = monthly["Date"].dt.to_timestamp()

            fig_line = px.line(
                monthly.melt(id_vars="Date", var_name="Type", value_name="Amount"),
                x="Date", y="Amount", color="Type", markers=True,
                color_discrete_sequence=["#27ae60", "#c0392b"],
                height=420
            )
            fig_line.update_layout(template="plotly_white", hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {str(e)}")
            st.info("Try refreshing or check date values in sheet.")
    else:
        st.info("Date column is not in datetime format → monthly trend unavailable.")

# ────────────────────────────────────────────────
st.subheader("Expense Breakdown by Category & Subcategory")

exp = df[df["Type"] == "Expense"]
if not exp.empty:
    fig_sun = px.sunburst(
        exp, path=["Category", "Subcategory"], values="Amount",
        color="Category", height=520, color_continuous_scale="RdBu"
    )
    fig_sun.update_layout(template="plotly_white", margin=dict(t=30,l=10,r=10,b=10))
    st.plotly_chart(fig_sun, use_container_width=True)
else:
    st.info("No expenses recorded yet.")

# ────────────────────────────────────────────────
st.subheader("AI-Generated Insights")
summary_text = f"House {house}:\nIncome: ₹{income:,.0f}\nExpense: ₹{expense:,.0f}\nBalance: ₹{balance:,.0f}"
insights = generate_insights(summary_text)

if insights:
    st.markdown(insights)
else:
    st.info("No insights available right now.")

# ────────────────────────────────────────────────
st.subheader("Recent Transactions")
if not df.empty:
    st.dataframe(
        df.sort_values("Date", ascending=False).head(12)[
            ["Date", "Type", "Amount", "Category", "Subcategory", "Description"]
        ].style.format({
            "Date": "{:%Y-%m-%d}",
            "Amount": "₹{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No transactions found for this house.")