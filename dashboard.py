import streamlit as st
import time
from datetime import datetime, timezone, timedelta

from styles import STYLES_DARK, STYLES_LIGHT
from api_clients import fetch_prices, fetch_history, REFRESH_INTERVAL
from components import render_card, render_summary, render_chart

st.set_page_config(page_title="Gold Tracker MY", layout="wide", page_icon="🥇")

# ---------------- SESSION ----------------
for key, val in [("data", None), ("last_fetch", 0), ("history", None), ("light_mode", False)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------- THEME ----------------
if st.session_state.light_mode:
    st.markdown(STYLES_LIGHT, unsafe_allow_html=True)
else:
    st.markdown(STYLES_DARK, unsafe_allow_html=True)

# ---------------- MARKET STATUS ----------------
def get_malaysia_time():
    return datetime.now(timezone.utc) + timedelta(hours=8)

def get_market_status():
    myt = get_malaysia_time()
    if myt.weekday() >= 5:
        return "weekend", "🗓 Weekend · Market Closed", "market-weekend", "dot-weekend"
    if myt.hour < 8 or myt.hour >= 18:
        if myt.hour >= 18:
            return "closed", "Market Closed · Opens at 8:00 AM", "market-closed", "dot-closed"
        else:
            return "closed", "Market Closed · Opens at 8:00 AM", "market-closed", "dot-closed"
    return "open", "Market Open · Closes at 6:00 PM", "market-open", "dot-open"

# ---------------- HEADER ----------------
st.markdown("""
<div class="header-bar">
    <div class="header-title">🥇 GOLD TRACKER MY</div>
    <div class="header-sub">Live prices · Malaysian banks</div>
</div>
""", unsafe_allow_html=True)

# ---------------- CONTROLS ROW ----------------
col_status, col_space, col_toggle, col_refresh = st.columns([4, 10 , 1, 1])

status, status_text, status_class, dot_class = get_market_status()
with col_status:
    st.markdown(f"""
    <div class="market-status {status_class}">
        <span class="dot {dot_class}"></span>
        {status_text}
    </div>
    """, unsafe_allow_html=True)

with col_toggle:
    light = st.toggle("☀️", value=st.session_state.light_mode, key="theme_toggle")
    if light != st.session_state.light_mode:
        st.session_state.light_mode = light
        st.rerun()

with col_refresh:
    if st.button("↺"):
        st.session_state.last_fetch = 0
        st.session_state.history = None

# ---------------- FETCH PRICES ----------------
current_time = time.time()
if st.session_state.data is None or current_time - st.session_state.last_fetch > REFRESH_INTERVAL:
    with st.spinner("Fetching prices..."):
        try:
            st.session_state.data = fetch_prices()
            st.session_state.last_fetch = current_time
        except Exception as e:
            st.error(f"Failed to fetch prices: {e}")

data = st.session_state.data

# ---------------- DISPLAY ----------------
if data:
    prices   = data.get("prices", {})
    analysis = data.get("analysis", {})
    best_buy  = analysis.get("best_buy")  if isinstance(analysis, dict) else None
    best_sell = analysis.get("best_sell") if isinstance(analysis, dict) else None

    banks = list(prices.items())
    cols  = st.columns(2)

    for idx, (bank, info) in enumerate(banks):
        render_card(
            col=cols[idx % 2],
            bank=bank,
            info=info,
            is_buy=bank == best_buy,
            is_sell=bank == best_sell
        )

    render_summary(best_buy, best_sell)

    last_updated = time.strftime("%d %b %Y, %H:%M:%S", time.localtime(st.session_state.last_fetch))
    st.caption(f"Page last refreshed: {last_updated}")

    # ---------------- HISTORY CHART ----------------
    st.markdown("---")
    st.markdown('<div class="section-label">Price Trends — Today</div>', unsafe_allow_html=True)

    if st.session_state.history is None:
        with st.spinner("Loading history..."):
            try:
                st.session_state.history = fetch_history()
            except Exception as e:
                st.error(f"History fetch failed: {e}")

    render_chart(st.session_state.history, light_mode=st.session_state.light_mode)

else:
    st.warning("No data available. The server may be waking up — try refreshing in 30 seconds.")