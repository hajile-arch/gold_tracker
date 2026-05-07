import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Gold Tracker", layout="wide")

st.title("💰 Gold Price Dashboard")
st.caption("Live prices from Malaysian banks")

API_URL = "https://just-basic-gold-tracking.onrender.com"
REFRESH_INTERVAL = 4 * 60 * 60  # 4 hours

# ---------------- SESSION ----------------
if "data" not in st.session_state:
    st.session_state.data = None

if "last_fetch" not in st.session_state:
    st.session_state.last_fetch = 0

# ---------------- REFRESH BUTTON ----------------
colA, colB = st.columns([6,1])
with colB:
    if st.button("🔄"):
        st.session_state.last_fetch = 0

# ---------------- FETCH ----------------
current_time = time.time()

if (
    st.session_state.data is None
    or current_time - st.session_state.last_fetch > REFRESH_INTERVAL
):
    with st.spinner("Fetching latest prices..."):
        try:
            response = requests.get(API_URL, timeout=60)
            response.raise_for_status()
            st.session_state.data = response.json()
            st.session_state.last_fetch = current_time
        except Exception as e:
            st.error(f"Error: {e}")

data = st.session_state.data

# ---------------- STYLE ----------------
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #111827;
    border: 1px solid #1f2937;
    margin-bottom: 15px;
}
.price {
    font-size: 28px;
    font-weight: bold;
}
.label {
    color: #9ca3af;
    font-size: 14px;
}
.best {
    color: #10b981;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DISPLAY ----------------
if data:
    prices = data.get("prices", {})
    analysis = data.get("analysis", {})

    banks = list(prices.items())

    for i in range(0, len(banks), 2):
        col1, col2 = st.columns(2)

        # LEFT CARD
        bank1, info1 = banks[i]
        with col1:
            st.markdown(f"""
            <div class="card">
                <h3>{bank1}</h3>
                <div class="label">Selling</div>
                <div class="price">RM {info1.get("selling", "N/A")}</div>
                <div class="label">Buying</div>
                <div class="price">RM {info1.get("buying", "N/A")}</div>
                <br>
                <div class="label">{info1.get("time", "")}</div>
            </div>
            """, unsafe_allow_html=True)

            if isinstance(analysis, dict):
                if analysis.get("best_buy") == bank1:
                    st.markdown('<div class="best">💡 Best to BUY</div>', unsafe_allow_html=True)
                if analysis.get("best_sell") == bank1:
                    st.markdown('<div class="best">💰 Best to SELL</div>', unsafe_allow_html=True)

        # RIGHT CARD
        if i + 1 < len(banks):
            bank2, info2 = banks[i + 1]
            with col2:
                st.markdown(f"""
                <div class="card">
                    <h3>{bank2}</h3>
                    <div class="label">Selling</div>
                    <div class="price">RM {info2.get("selling", "N/A")}</div>
                    <div class="label">Buying</div>
                    <div class="price">RM {info2.get("buying", "N/A")}</div>
                    <br>
                    <div class="label">{info2.get("time", "")}</div>
                </div>
                """, unsafe_allow_html=True)

                if isinstance(analysis, dict):
                    if analysis.get("best_buy") == bank2:
                        st.markdown('<div class="best">💡 Best to BUY</div>', unsafe_allow_html=True)
                    if analysis.get("best_sell") == bank2:
                        st.markdown('<div class="best">💰 Best to SELL</div>', unsafe_allow_html=True)

    st.divider()

    # SUMMARY
    if isinstance(analysis, dict):
        st.success(f"🏆 Best BUY: {analysis.get('best_buy')}")
        st.success(f"🏆 Best SELL: {analysis.get('best_sell')}")

    # LAST REFRESH
    last_updated = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(st.session_state.last_fetch)
    )
    st.caption(f"Last updated: {last_updated}")

    # ---------------- HISTORY CHART & DOWNLOAD ----------------
    st.divider()
    st.subheader("📈 Today's Price Trends")
    
    with st.spinner("Loading history..."):
        try:
            history_response = requests.get(f"{API_URL}/history", timeout=15)
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                
                if history_data and len(history_data) > 0:
                    # Parse the JSON into a format Pandas loves
                    chart_rows = []
                    for entry in history_data:
                        row = {"Time": entry.get("time", "Unknown")}
                        for bank, details in entry.get("prices", {}).items():
                            if details.get("selling"):
                                row[f"{bank} (Sell)"] = details["selling"]
                        chart_rows.append(row)
                        
                    df = pd.DataFrame(chart_rows)
                    
                    if not df.empty:
                        # Set 'Time' as the X-axis
                        df.set_index("Time", inplace=True) 
                        
                        # Render the chart
                        st.line_chart(df)
                        
                        # Render the download button
                        csv_data = df.to_csv().encode('utf-8')
                        st.download_button(
                            label="📥 Download Today's Data (CSV)",
                            data=csv_data,
                            file_name=f"gold_prices_{time.strftime('%Y-%m-%d')}.csv",
                            mime="text/csv",
                        )
                else:
                    st.info("Not enough data to draw a chart yet. The bot is collecting data in the background!")
            else:
                st.warning(f"Could not fetch history. Status Code: {history_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the history API: {e}")

else:
    st.warning("No data available.")