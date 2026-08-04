import streamlit as st
from config.settings import APP_NAME
from services.sheets_service import ensure_sheet_exists, get_service

st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- INITIALIZE SHEET ON START ----------
@st.cache_resource
def initialize_app():
    try:
        service = get_service()
        ensure_sheet_exists(service)
    except Exception as e:
        pass
    return True

initialize_app()
# -----------------------------------------------

# Predefined houses (only these 100 are allowed)
HOUSES = [f"{i}/100" for i in range(1, 101)]

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(
    """
## Finora
**AI-Powered Communal Finance Tracker**
""",
    unsafe_allow_html=True
)

st.sidebar.divider()

# Reset helper button (very useful during development / debugging)
if st.sidebar.button("🔄 Reset Session", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.sidebar.success("Session cleared. Refresh page (Ctrl+Shift+R).")
    st.rerun()

# ---------------- MAIN PAGE ----------------
st.title("Welcome to Finora Communal Tracker")
st.markdown("Finance tracking system for one panchayat (100 houses)")

st.divider()

col_mode, col_house = st.columns([1, 2])

with col_mode:
    st.subheader("Select Mode")
    mode = st.radio(
        "Choose your access level",
        options=["House User", "Government View"],
        captions=[
            "For individual house owners/residents",
            "For panchayat/municipality officials (aggregate view)"
        ],
        horizontal=True,
        key="mode_radio"
    )

# Map radio to internal mode value
if mode == "House User":
    current_mode = "House"
else:
    current_mode = "Government"

# Handle mode change
if "mode" not in st.session_state or st.session_state.mode != current_mode:
    st.session_state.mode = current_mode
    st.session_state.house_no = None    # Force reset house when mode changes
    st.rerun()

# House selection (only shown in House mode)
if st.session_state.mode == "House":
    with col_house:
        st.subheader("Select Your House")
        
        selected_house = st.selectbox(
            "House Number",
            options=["— Please select your house —"] + HOUSES,
            index=0,
            key="house_select",
            help="Choose your house number from the list"
        )
        
        if selected_house != "— Please select your house —":
            if st.session_state.get("house_no") != selected_house:
                st.session_state.house_no = selected_house
                st.success(f"Logged in as **House {selected_house}**")
                st.rerun()
        else:
            st.info("Please select your house number to continue.")

# Show sidebar navigation based on mode
if st.session_state.mode == "House" and st.session_state.house_no:
    st.sidebar.markdown(f"**Active house:** {st.session_state.house_no}")
    st.sidebar.page_link("pages/Add_Transaction.py", label="➕ Add Transaction", icon="📝")
    st.sidebar.page_link("pages/Analytics.py", label="📊 My Analytics", icon="📈")
    
elif st.session_state.mode == "Government":
    st.sidebar.markdown("**Government / Panchayat View**")
    st.sidebar.page_link("pages/Aggregate_Analytics.py", label="📊 Aggregate Analytics", icon="🌐")
    # st.sidebar.page_link("pages/Scheme_Insights.py", label="💡 Scheme Insights", icon="🧠")

st.sidebar.divider()
st.sidebar.caption("Data is stored securely in Google Sheets")

# Feature highlights
st.markdown("### Key Features")
cols = st.columns(3)

with cols[0]:
    st.markdown("""
    **House Users**
    - Add income & expenses naturally
    - See personal charts & balance
    """)

with cols[1]:
    st.markdown("""
    **Government View**
    - See data from all 100 houses
    - Category breakdowns, heatmaps
    - AI suggested schemes
    """)

with cols[2]:
    st.markdown("""
    **AI Assistance**
    - Smart transaction parsing
    - Gemini-powered insights
    """)

st.info("Use the **Reset Session** button in sidebar if the house selection feels stuck.", icon="ℹ️")