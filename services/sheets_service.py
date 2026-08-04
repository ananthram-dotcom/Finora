import os
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config.settings import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_ID
from core.logger import logger

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME = "Expenses"
HEADERS = ["House_No", "Date", "Type", "Amount", "Category", "Subcategory", "Description"]
LOCAL_CSV_PATH = os.path.join("data", "transactions.csv")

def ensure_local_csv():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(LOCAL_CSV_PATH):
        df = pd.DataFrame(columns=HEADERS)
        df.to_csv(LOCAL_CSV_PATH, index=False)
        logger.info("Local transactions.csv initialized.")

def get_service():
    import streamlit as st
    # 1. Try Streamlit secrets dict (for Streamlit Community Cloud)
    try:
        if "gcp_service_account" in st.secrets:
            creds_info = dict(st.secrets["gcp_service_account"])
            creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
            return build("sheets", "v4", credentials=creds)
    except Exception:
        pass

    # 2. Try credentials file path
    if GOOGLE_CREDENTIALS_PATH and os.path.exists(GOOGLE_CREDENTIALS_PATH):
        try:
            creds = Credentials.from_service_account_file(
                GOOGLE_CREDENTIALS_PATH,
                scopes=SCOPES
            )
            return build("sheets", "v4", credentials=creds)
        except Exception as e:
            logger.warning(f"Could not build Google Sheets service: {e}")
            return None
    return None

def ensure_sheet_exists(service=None):
    ensure_local_csv()
    if not GOOGLE_SHEET_ID:
        logger.info("GOOGLE_SHEET_ID not configured. Operating in local CSV mode.")
        return False
    if service is None:
        service = get_service()
    if service is None:
        return False

    try:
        spreadsheet = service.spreadsheets().get(
            spreadsheetId=GOOGLE_SHEET_ID
        ).execute()

        sheets = [s["properties"]["title"] for s in spreadsheet["sheets"]]

        if SHEET_NAME not in sheets:
            service.spreadsheets().batchUpdate(
                spreadsheetId=GOOGLE_SHEET_ID,
                body={
                    "requests": [{
                        "addSheet": {
                            "properties": {"title": SHEET_NAME}
                        }
                    }]
                }
            ).execute()

            service.spreadsheets().values().update(
                spreadsheetId=GOOGLE_SHEET_ID,
                range=f"{SHEET_NAME}!A1:G1",
                valueInputOption="RAW",
                body={"values": [HEADERS]}
            ).execute()

            logger.info("Expenses sheet created with headers")
        return True
    except Exception as e:
        logger.warning(f"Google Sheets initialization/access failed ({e}). Operating in local CSV mode.")
        return False

def append_transaction(txn: dict):
    ensure_local_csv()
    # Always append to local CSV
    new_row = pd.DataFrame([[
        txn["house_no"],
        txn["date"],
        txn["type"],
        txn["amount"],
        txn["category"],
        txn["subcategory"],
        txn["description"]
    ]], columns=HEADERS)
    
    new_row.to_csv(LOCAL_CSV_PATH, mode='a', header=False, index=False)

    # If Google Sheet ID is configured, also attempt to write to Google Sheets
    if GOOGLE_SHEET_ID:
        try:
            service = get_service()
            if service and ensure_sheet_exists(service):
                values = [[
                    txn["house_no"],
                    txn["date"],
                    txn["type"],
                    txn["amount"],
                    txn["category"],
                    txn["subcategory"],
                    txn["description"]
                ]]
                service.spreadsheets().values().append(
                    spreadsheetId=GOOGLE_SHEET_ID,
                    range=f"{SHEET_NAME}!A:G",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": values}
                ).execute()
                logger.info("Transaction appended to Google Sheets successfully")
        except Exception as e:
            logger.warning(f"Failed to append transaction to Google Sheets ({e}). Saved locally.")

    logger.info("Transaction saved successfully.")

def read_transactions():
    ensure_local_csv()
    
    # Try reading from Google Sheets if configured
    if GOOGLE_SHEET_ID:
        try:
            service = get_service()
            if service and ensure_sheet_exists(service):
                result = service.spreadsheets().values().get(
                    spreadsheetId=GOOGLE_SHEET_ID,
                    range=f"{SHEET_NAME}!A:G"
                ).execute()

                values = result.get("values", [])
                if len(values) > 1:
                    df = pd.DataFrame(values[1:], columns=values[0])
                    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
                    return df
        except Exception as e:
            logger.warning(f"Failed to read from Google Sheets ({e}). Reading from local CSV instead.")

    # Fallback to local CSV
    if os.path.exists(LOCAL_CSV_PATH):
        try:
            df = pd.read_csv(LOCAL_CSV_PATH, dtype=str)
            if df.empty or len(df.columns) < len(HEADERS):
                return pd.DataFrame(columns=HEADERS)
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
            return df
        except Exception as e:
            logger.error(f"Failed to read local CSV: {e}")

    return pd.DataFrame(columns=HEADERS)