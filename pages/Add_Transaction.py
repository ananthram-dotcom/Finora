import sys
from pathlib import Path

# ---------- HARD ROOT PATH FIX (DO NOT REMOVE) ----------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
# ------------------------------------------------------

import streamlit as st
from services.ai_service import parse_with_ai
from core.parser import fallback_parse
from core.validators import validate_transaction
from services.sheets_service import append_transaction

st.set_page_config(page_title="Add Transaction", layout="centered")

if "house_no" not in st.session_state or not st.session_state.house_no:
    st.error("Please enter your House Number on the home page.")
    st.stop()

st.markdown("## Add a Transaction")
st.caption(f"House {st.session_state.house_no}: Type naturally — Finora understands your message.")

st.divider()

# Chat history (UI only)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(msg)

user_message = st.chat_input("e.g. Paid rent 3000")

if user_message:
    st.session_state.chat_history.append(("user", user_message))

    with st.chat_message("assistant"):
        with st.spinner("Analyzing transaction..."):
            txn = parse_with_ai(user_message)
            if not txn:
                txn = fallback_parse(user_message)

            if not txn:
                st.error("Unable to understand this transaction.")
            else:
                txn["house_no"] = st.session_state.house_no
                valid, msg = validate_transaction(txn)
                if not valid:
                    st.error(msg)
                else:
                    append_transaction(txn)
                    st.success("Transaction saved successfully")

                    st.markdown("**Detected transaction details:**")
                    st.json(txn)

    st.session_state.chat_history.append(
        ("assistant", "Transaction processed and saved.")
    )