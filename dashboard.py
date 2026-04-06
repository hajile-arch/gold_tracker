import streamlit as st
import requests
import time

st.title("💰 Gold Prices from 4 Institutions")

API_URL = "https://just-basic-gold-tracking.onrender.com"

REFRESH_INTERVAL = 4 * 60 * 60  # 4 hours (in seconds)

# ---------------- SESSION STATE ----------------
if "data" not in st.session_state:
    st.session_state.data = None

if "last_fetch" not in st.session_state:
    st.session_state.last_fetch = 0

# ---------------- REFRESH BUTTON ----------------
if st.button("🔄 Refresh Now"):
    st.session_state.last_fetch = 0  # force refresh

# ---------------- FETCH LOGIC ----------------
current_time = time.time()

if (
    st.session_state.data is None
    or current_time - st.session_state.last_fetch > REFRESH_INTERVAL
):
    with st.spinner("Fetching live gold prices... (may take a while if server is sleeping)"):
        try:
            response = requests.get(API_URL, timeout=60)
            response.raise_for_status()
            st.session_state.data = response.json()
            st.session_state.last_fetch = current_time

        except requests.exceptions.Timeout:
            st.error("Server took too long to respond. Try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")

# ---------------- DISPLAY DATA ----------------
data = st.session_state.data

if data:
    prices = data.get("prices", {})
    analysis = data.get("analysis", {})

    banks = list(prices.items())

    # -------- GRID (2x2) --------
    for i in range(0, len(banks), 2):
        col1, col2 = st.columns(2)

        # LEFT CARD
        bank1, info1 = banks[i]
        with col1:
            st.subheader(bank1)
            st.metric("Selling", info1.get("selling", "N/A"))
            st.metric("Buying", info1.get("buying", "N/A"))
            st.caption(info1.get("time", "N/A"))

            if isinstance(analysis, dict):
                if analysis.get("best_buy") == bank1:
                    st.success("💡 Best to BUY here")
                if analysis.get("best_sell") == bank1:
                    st.success("💰 Best to SELL here")

        # RIGHT CARD
        if i + 1 < len(banks):
            bank2, info2 = banks[i + 1]
            with col2:
                st.subheader(bank2)
                st.metric("Selling", info2.get("selling", "N/A"))
                st.metric("Buying", info2.get("buying", "N/A"))
                st.caption(info2.get("time", "N/A"))

                if isinstance(analysis, dict):
                    if analysis.get("best_buy") == bank2:
                        st.success("💡 Best to BUY here")
                    if analysis.get("best_sell") == bank2:
                        st.success("💰 Best to SELL here")

    st.divider()

    # -------- ANALYSIS SUMMARY --------
    if isinstance(analysis, dict):
        st.info(f"🏆 Best place to BUY: {analysis.get('best_buy')}")
        st.info(f"🏆 Best place to SELL: {analysis.get('best_sell')}")
    elif isinstance(analysis, str):
        st.warning(analysis)

    # -------- LAST UPDATED --------
    last_updated_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(st.session_state.last_fetch)
    )
    st.caption(f"Last refreshed: {last_updated_time}")

else:
    st.warning("No data available yet.")