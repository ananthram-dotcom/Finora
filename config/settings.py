import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_config_val(key: str, default: str = "") -> str:
    # 1. Environment variables / .env
    val = os.getenv(key)
    if val is not None and val != "":
        return val
    # 2. Streamlit Secrets (for Streamlit Community Cloud hosting)
    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default

GOOGLE_CREDENTIALS_PATH = get_config_val("GOOGLE_CREDENTIALS_PATH", "credentials/service_account.json")
GOOGLE_SHEET_ID = get_config_val("GOOGLE_SHEET_ID", "")
ENABLE_AI = get_config_val("ENABLE_AI", "false").lower() == "true"
GEMINI_API_KEY = get_config_val("GEMINI_API_KEY", "")
APP_NAME = "Finora – AI-Powered Communal Finance Tracker"
LOG_FILE = "logs/finora.log"