import streamlit as st
import time

from styles import STYLES
from api_clients import fetch_prices, fetch_history, REFRESH_INTERVAL
from components import render_card, render_summary, render_chart

st.set_page_config(page_title="Gold Tracker MY", layout="wide", page_icon="🥇")
st.markdown(STYLES, unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="header-bar">
    <div class="header-title">🥇 GOLD TRACKER MY</div>
    <div class="header-sub">Live prices · Malaysian banks</div>
</div>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
for key, val in [("data", None), ("last_fetch", 0), ("history", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------- REFRESH ----------------
col_space, col_btn = st.columns([8, 1])
with col_btn:
    if st.button("↺ Refresh"):
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

    render_chart(st.session_state.history)

else:
    st.warning("No data available. The server may be waking up — try refreshing in 30 seconds.")