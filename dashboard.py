import streamlit as st
import requests
import time
import pandas as pd
import plotly.graph_objects as go
import re

st.set_page_config(page_title="Gold Tracker MY", layout="wide", page_icon="🥇")

# ---------------- STYLE ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0a0a0a;
    color: #e5e5e5;
}

h1, h2, h3 { font-family: 'Syne', sans-serif; }

.stApp { background-color: #0a0a0a; }

/* Top header */
.header-bar {
    border-bottom: 1px solid #222;
    padding-bottom: 12px;
    margin-bottom: 24px;
}
.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #f5c842;
}
.header-sub {
    font-size: 12px;
    color: #555;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Bank cards */
.card {
    padding: 20px 24px;
    border-radius: 4px;
    background-color: #111;
    border: 1px solid #1e1e1e;
    border-left: 3px solid #333;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.card.best-buy  { border-left-color: #f5c842; }
.card.best-sell { border-left-color: #4ade80; }
.card.both      { border-left-color: #60a5fa; }

.bank-name {
    font-family: 'Syne', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.price-row {
    display: flex;
    gap: 32px;
    margin-bottom: 10px;
}
.price-block {}
.price-label {
    font-size: 10px;
    color: #555;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.price-value {
    font-size: 26px;
    font-weight: 500;
    color: #f0f0f0;
}
.price-value span {
    font-size: 12px;
    color: #555;
    margin-right: 2px;
}

.card-time {
    font-size: 11px;
    color: #3a3a3a;
    margin-top: 10px;
    border-top: 1px solid #1a1a1a;
    padding-top: 8px;
}

.badge {
    display: inline-block;
    font-size: 10px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 2px;
    margin-right: 6px;
    font-weight: 500;
}
.badge-buy  { background: #2a2000; color: #f5c842; border: 1px solid #f5c842; }
.badge-sell { background: #002a10; color: #4ade80; border: 1px solid #4ade80; }

/* Spread pill */
.spread {
    font-size: 11px;
    color: #555;
    margin-top: 4px;
}
.spread b { color: #e05a5a; }

/* Summary row */
.summary-row {
    display: flex;
    gap: 16px;
    margin: 20px 0;
}
.summary-pill {
    padding: 10px 18px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
}
.summary-pill.buy  { background: #1a1400; border: 1px solid #f5c842; color: #f5c842; }
.summary-pill.sell { background: #001a0a; border: 1px solid #4ade80; color: #4ade80; }

/* N/A dimming */
.na { color: #2a2a2a !important; }

/* Divider */
hr { border-color: #1a1a1a; }

/* Section label */
.section-label {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #333;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

API_URL = "https://just-basic-gold-tracking.onrender.com"
REFRESH_INTERVAL = 15 * 60
def clean_time(t):
    if not t or t == "N/A":
        return ""
    # Strip ALL html tags, not just inner ones
    return re.sub(r'<[^>]+>', '', str(t)).strip()

# ---------------- SESSION ----------------
for key, val in [("data", None), ("last_fetch", 0), ("history", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------- HEADER ----------------
st.markdown("""
<div class="header-bar">
    <div class="header-title">🥇 GOLD TRACKER MY</div>
    <div class="header-sub">Live prices · Malaysian banks</div>
</div>
""", unsafe_allow_html=True)

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
            r = requests.get(API_URL, timeout=60)
            r.raise_for_status()
            st.session_state.data = r.json()
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
        selling = info.get("selling")
        buying  = info.get("buying")
        updated = info.get("time", "")
        print(f"[DEBUG] {bank} time raw value:", repr(updated))  # ADD THIS

        is_buy  = bank == best_buy
        is_sell = bank == best_sell
        card_class = "card"
        if is_buy and is_sell: card_class += " both"
        elif is_buy:           card_class += " best-buy"
        elif is_sell:          card_class += " best-sell"

        sell_html = f'<span>RM</span>{selling:.2f}' if selling else '<span class="na">—</span>'
        buy_html  = f'<span>RM</span>{buying:.2f}'  if buying  else '<span class="na">—</span>'

        spread_html = ""
        unit = info.get("unit")
        orig_sell = info.get("original_selling")
        orig_buy = info.get("original_buying")
        unit_html = ""
        if unit:
            unit_html = f'<p style="font-size:11px;color:#555;margin-top:4px;">⚠️ Quoted per {unit} · Original: RM {orig_sell} / RM {orig_buy}</p>'
        if selling and buying:
            spread = selling - buying
            spread_html = f'<div class="spread">Spread: <b>RM {spread:.2f}</b></div>'

        badges = ""
        if is_buy:  badges += '<span class="badge badge-buy">Best Buy</span>'
        if is_sell: badges += '<span class="badge badge-sell">Best Sell</span>'

        time_display = clean_time(updated)
        time_html = f'<p style="font-size:11px;color:#3a3a3a;margin-top:10px;border-top:1px solid #1a1a1a;padding-top:8px;">{clean_time(updated)}</p>' if time_display else "" 
        print(f"[DEBUG] {bank} time_html:", repr(time_html))
        print(f"[DEBUG] {bank} sell_html:", repr(sell_html))
        print(f"[DEBUG] {bank} buy_html:", repr(buy_html))
        print(f"[DEBUG] {bank} spread_html:", repr(spread_html))
        print(f"[DEBUG] {bank} badges:", repr(badges))
        # st.markdown(time_html, unsafe_allow_html=True)
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="{card_class}">
                <div class="bank-name">{bank}</div>
                <div class="price-row">
                    <div class="price-block">
                        <div class="price-label">Selling</div>
                        <div class="price-value">{sell_html}</div>
                    </div>
                    <div class="price-block">
                        <div class="price-label">Buying</div>
                        <div class="price-value">{buy_html}</div>
                    </div>
                </div>
                {spread_html}
                {unit_html}
                {badges}
            </div>
            """, unsafe_allow_html=True)
            
            if time_html:
                st.caption(clean_time(updated))

    # ---------------- SUMMARY ----------------
    if best_buy or best_sell:
        st.markdown(f"""
        <div class="summary-row">
            <div class="summary-pill buy">💡 Best to BUY &nbsp;·&nbsp; {best_buy}</div>
            <div class="summary-pill sell">💰 Best to SELL &nbsp;·&nbsp; {best_sell}</div>
        </div>
        """, unsafe_allow_html=True)

    last_updated = time.strftime("%d %b %Y, %H:%M:%S", time.localtime(st.session_state.last_fetch))
    st.caption(f"Page last refreshed: {last_updated}")

    # ---------------- HISTORY CHART ----------------
    st.markdown("---")
    st.markdown('<div class="section-label">Price Trends — Today</div>', unsafe_allow_html=True)

    if st.session_state.history is None:
        with st.spinner("Loading history..."):
            try:
                hr = requests.get(f"{API_URL}/history/all", timeout=15)
                if hr.status_code == 200:
                    st.session_state.history = hr.json()
            except Exception as e:
                st.error(f"History fetch failed: {e}")

    history_data = st.session_state.history

    if history_data and len(history_data) > 1:
        chart_rows = []
        for entry in history_data:
            row = {"Time": entry.get("time", "?")}
            for bank, details in entry.get("prices", {}).items():
                sell = details.get("selling")
                buy  = details.get("buying")
                if sell: row[f"{bank} Sell"] = sell
                if buy:  row[f"{bank} Buy"]  = buy
            chart_rows.append(row)

        df = pd.DataFrame(chart_rows).set_index("Time")

        # Separate sell and buy columns
        sell_cols = [c for c in df.columns if "Sell" in c]
        buy_cols  = [c for c in df.columns if "Buy"  in c]

        # Color palette
        bank_colors = {
            "CIMB":    "#f5c842",
            "UOB":     "#4ade80",
            "Maybank": "#60a5fa",
            "Pbe":     "#f97316",
            "RHB":     "#e11d48",
            "HSBC":    "#8b0202",
        }

        tab_sell, tab_buy, tab_all = st.tabs(["Selling Prices", "Buying Prices", "All"])

        def make_chart(cols_to_plot, title):
            fig = go.Figure()
            all_vals = []

            for col in cols_to_plot:
                if col not in df.columns:
                    continue
                series = df[col].dropna()
                if series.empty:
                    continue
                all_vals.extend(series.tolist())
                bank_name = col.split(" ")[0]
                color = bank_colors.get(bank_name, "#888")
                line_dash = "dot" if "Buy" in col else "solid"

                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode="lines+markers",
                    name=col,
                    line=dict(color=color, width=2, dash=line_dash),
                    marker=dict(size=5),
                    connectgaps=False,
                    hovertemplate=f"<b>{col}</b><br>Time: %{{x}}<br>Price: RM %{{y:.2f}}<extra></extra>"
                ))

            if all_vals:
                y_min = min(all_vals) - 1
                y_max = max(all_vals) + 1
            else:
                y_min, y_max = 550, 650

            fig.update_layout(
                paper_bgcolor="#0a0a0a",
                plot_bgcolor="#0f0f0f",
                font=dict(family="DM Mono, monospace", color="#888", size=11),
                yaxis=dict(
                    range=[y_min, y_max],
                    gridcolor="#1a1a1a",
                    tickprefix="RM ",
                    tickformat=".2f",
                    title=None,
                ),
                xaxis=dict(
                    gridcolor="#1a1a1a",
                    title=None,
                ),
                legend=dict(
                    bgcolor="#111",
                    bordercolor="#222",
                    borderwidth=1,
                    font=dict(size=11),
                ),
                hovermode="x unified",
                height=380,
                margin=dict(l=10, r=10, t=20, b=10),
            )
            return fig

        with tab_sell:
            st.plotly_chart(make_chart(sell_cols, "Selling"), width='stretch')

        with tab_buy:
            st.plotly_chart(make_chart(buy_cols, "Buying"), width='stretch')

        with tab_all:
            st.plotly_chart(make_chart(sell_cols + buy_cols, "All"), width='stretch')

        # Download
        csv_data = df.to_csv().encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"gold_prices_{time.strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
        )

    elif history_data and len(history_data) == 1:
        st.info("Only 1 data point so far — chart needs at least 2. Check back soon.")
    else:
        st.info("No history yet. The bot is collecting data in the background.")

else:
    st.warning("No data available. The server may be waking up — try refreshing in 30 seconds.")