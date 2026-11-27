import re
from datetime import date, timedelta
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from api_clients import fetch_news
from cache import get_malaysia_time

BANK_COLORS = {
    "CIMB":    "#f5c842",
    "UOB":     "#4ade80",
    "Maybank": "#60a5fa",
    "Pbe":     "#f97316",
    "RHB":     "#e11d48",
    "HSBC":    "#8b0202",
}


def clean_time(t):
    if not t or t == "N/A":
        return ""
    return re.sub(r'<[^>]+>', '', str(t)).strip()


def render_card(col, bank, info, is_buy, is_sell, is_stale=False):
    selling = info.get("selling")
    buying  = info.get("buying")
    updated = info.get("time", "")
    unit    = info.get("unit")
    orig_sell = info.get("original_selling")
    orig_buy  = info.get("original_buying")

    card_class = "card"
    if is_buy and is_sell: card_class += " both"
    elif is_buy:           card_class += " best-buy"
    elif is_sell:          card_class += " best-sell"

    sell_html = f'<span>RM</span>{selling:.2f}' if selling else '<span class="na">—</span>'
    buy_html  = f'<span>RM</span>{buying:.2f}'  if buying  else '<span class="na">—</span>'

    spread_html = ""
    if selling and buying:
        spread = selling - buying
        spread_html = f'<div class="spread">Spread: <b>RM {spread:.2f}</b></div>'

    badges = ""
    if is_buy:  badges += '<span class="badge badge-buy">Best Buy</span>'
    if is_sell: badges += '<span class="badge badge-sell">Best Sell</span>'

    time_display = clean_time(updated)
    if is_stale:
        time_display += " · ⚠️ Outdated quote, not used for Best Buy/Sell"

    with col:
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
            {badges}
        </div>
        """, unsafe_allow_html=True)

        if time_display:
            if unit:
                st.caption(f"{time_display} · ⚠️ Quoted per {unit} · Original: RM {orig_sell} / RM {orig_buy}")
            else:
                st.caption(time_display)


VERDICT = {
    "buy":  {"good": "Good time to buy", "neutral": "Normal price", "wait": "Pricey, maybe wait"},
    "sell": {"good": "Good time to sell", "neutral": "Normal price", "wait": "Low, maybe hold"},
}


def _decision_card(action, bank, price, s):
    s = s or {}
    verdict = s.get("verdict")
    label = "If you're buying" if action == "buy" else "If you're selling"
    bank_line = f"Best bank <b>{bank}</b> · RM {price:.2f}" if bank and price else "No valid quotes right now"

    if verdict in VERDICT[action]:
        headline, cls = VERDICT[action][verdict], verdict
        span = (s["high"] - s["low"]) or 1
        pos = lambda v: min(max((v - s["low"]) / span * 100, 0), 100)
        word = "were cheaper" if action == "buy" else "paid more"
        detail = (
            f'<div class="range"><div class="range-avg" style="left:{pos(s["avg"]):.0f}%"></div>'
            f'<div class="range-now" style="left:{pos(s["now"]):.0f}%"></div></div>'
            f'<div class="range-ends"><span>Low RM {s["low"]:.2f}</span><span>High RM {s["high"]:.2f}</span></div>'
            f'<div class="decision-note">Market today RM {s["now"]:.2f} vs avg RM {s["avg"]:.2f} · '
            f'{s["better_days_pct"]}% of the last {s["days"]} days {word}</div>'
        )
    elif verdict == "not_enough_data":
        headline, cls = "Collecting history", "none"
        detail = f'<div class="decision-note">Need a few more days of prices ({s.get("days", 0)} so far)</div>'
    else:
        headline, cls, detail = "Signal unavailable", "none", ""

    return (f'<div class="decision {cls}"><div class="decision-label">{label}</div>'
            f'<div class="decision-verdict">{headline}</div>'
            f'<div class="decision-bank">{bank_line}</div>{detail}</div>')


def render_decision(prices, best_buy, best_sell, signal):
    signal = signal or {}
    cards = (_decision_card("buy", best_buy, prices.get(best_buy, {}).get("selling"), signal.get("buy"))
             + _decision_card("sell", best_sell, prices.get(best_sell, {}).get("buying"), signal.get("sell")))
    st.markdown(f'<div class="decision-row">{cards}</div>', unsafe_allow_html=True)
    st.caption("Dot = today's market price (median across banks), tick = average. Based on past prices only, not financial advice.")


@st.cache_data(ttl=3600, show_spinner=False)
def _news(after, before):
    return fetch_news(after, before)


def _news_list(after, before):
    try:
        items = _news(after, before)
    except Exception as e:
        st.caption(f"News unavailable: {e}")
        return
    if not items:
        st.caption("No headlines found.")
    for n in items:
        title = n["title"].replace("[", "(").replace("]", ")").replace("$", r"\$")
        st.markdown(f"- [{title}]({n['link']}) · {n['source']} · {n['date']}")


def render_news(a):
    today = get_malaysia_time().date()
    st.markdown("**Latest headlines**")
    _news_list((today - timedelta(days=2)).isoformat(), (today + timedelta(days=1)).isoformat())

    for m in (a or {}).get("moves", []):
        arrow, word = ("▲", "rose") if m["pct"] > 0 else ("▼", "fell")
        day = date.fromisoformat(m["date"])
        with st.expander(f"{arrow} {abs(m['pct']):.2f}% · gold {word} on {day:%a %d %b}"):
            _news_list(m["prev"], (day + timedelta(days=1)).isoformat())
    st.caption("Headlines from around each date, matched by time only. They may not be the actual cause.")


def render_chart(history_data, light_mode=False):
    if not history_data:
        st.info("No history yet. The bot is collecting data in the background.")
        return

    if len(history_data) == 1:
        st.info("Only 1 data point so far — chart needs at least 2. Check back soon.")
        return

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
    sell_cols = [c for c in df.columns if "Sell" in c]
    buy_cols  = [c for c in df.columns if "Buy"  in c]

    tab_sell, tab_buy, tab_all = st.tabs(["Selling Prices", "Buying Prices", "All"])

    with tab_sell:
        st.plotly_chart(_make_chart(df, sell_cols, light_mode), width="stretch", theme=None)
    with tab_buy:
        st.plotly_chart(_make_chart(df, buy_cols, light_mode), width="stretch", theme=None)
    with tab_all:
        st.plotly_chart(_make_chart(df, sell_cols + buy_cols, light_mode), width="stretch", theme=None)

    csv_data = df.to_csv().encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"gold_prices_{get_malaysia_time().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )


def render_analytics(a, light_mode=False):
    if not a:
        return  # fetch failed, error already shown
    if not a.get("days"):
        st.info("No long-term history yet.")
        return

    fc = a.get("forecast")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{a['days']}-day change", f"{a['change_pct']:+.2f}%")
    fmt = lambda d: date.fromisoformat(d).strftime("%d %b")
    c2.metric(f"Cheapest day to buy · {fmt(a['best_buy_day']['date'])}", f"RM {a['best_buy_day']['price']:.2f}")
    c3.metric(f"Best day to sell · {fmt(a['best_sell_day']['date'])}", f"RM {a['best_sell_day']['price']:.2f}")
    if fc:
        c4.metric(f"Trend · last {fc['lookback_days']} days", f"RM {fc['slope_per_day']:+.2f}/day")

    df = pd.DataFrame(a["daily"]).set_index("date")
    df["avg7"] = df["sell"].rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["sell"], name="Selling (median)", line=dict(color="#f5c842", width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df["buy"], name="Buying (median)", line=dict(color="#4ade80", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=df["avg7"], name="Selling 7-day avg", line=dict(color="#60a5fa", width=1)))
    vals = df["sell"].tolist() + df["buy"].tolist()
    if fc:
        pts = pd.DataFrame(fc["points"])
        x_band = pts["date"].tolist() + pts["date"].tolist()[::-1]
        fig.add_trace(go.Scatter(x=x_band, y=pts["high"].tolist() + pts["low"].tolist()[::-1], fill="toself", mode="lines",
                                 fillcolor="rgba(245,200,66,0.15)", line=dict(width=0), name="Forecast range", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=pts["date"], y=pts["price"], name="Forecast (selling)", line=dict(color="#f5c842", dash="dash")))
        vals += pts["low"].tolist() + pts["high"].tolist()
    st.plotly_chart(_style(fig, vals, light_mode), width="stretch", theme=None)

    banks = pd.DataFrame(a["banks"]).T.sort_values("avg_spread_pct")
    st.table(pd.DataFrame({
        "Avg spread": banks["avg_spread_pct"].map("{:.2f}%".format),
        "Cheapest to buy (% of time)": banks["cheapest_pct"].map("{:.0f}%".format),
        "Best to sell to (% of time)": banks["best_sell_pct"].map("{:.0f}%".format),
    }))
    st.caption("Forecast is a straight-line trend through recent days, a rough guide only. "
               "Gold can move far outside the range. Not financial advice.")


def _make_chart(df, cols_to_plot, light_mode=False):
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
        color = BANK_COLORS.get(bank_name, "#0a0a0a")
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

    return _style(fig, all_vals, light_mode)


def _style(fig, all_vals, light_mode=False):
    bg = "#f5f5f0" if light_mode else "#0a0a0a"
    plot_bg = "#ffffff" if light_mode else "#0f0f0f"
    font_color = "#1a1a1a" if light_mode else "#e5e5e5"
    grid_color = "#e0e0d8" if light_mode else "#1a1a1a"
    legend_bg = "#ffffff" if light_mode else "#0a0a0a"
    legend_border = "#e0e0d8" if light_mode else "#1e1e1e"

    y_min = min(all_vals) - 1 if all_vals else 550
    y_max = max(all_vals) + 1 if all_vals else 650

    fig.update_layout(
        paper_bgcolor=bg,
        plot_bgcolor=plot_bg,
        font=dict(family="DM Mono, monospace", color=font_color, size=11),
        
        # FIX 1: Add automargin to give the Y-axis numbers breathing room
        yaxis=dict(
            range=[y_min, y_max], 
            gridcolor=grid_color, 
            tickprefix="RM ", 
            tickformat=".2f", 
            title=None,
            automargin=True
        ),
        
        # FIX 2: Prevent X-axis time text from bunching up
        xaxis=dict(
            gridcolor=grid_color, 
            title=None,
            tickangle=-45,          # Slant the time labels so they don't hit each other
            nticks=15,               # Cap the maximum number of visible time labels 
            automargin=True
        ),
        
        legend=dict(bgcolor=legend_bg, bordercolor=legend_border, borderwidth=1, font=dict(size=11)),
        hovermode="x unified",
        height=380,
        margin=dict(l=15, r=15, t=20, b=40), # Slightly increased bottom margin for the slanted text
    )
    return fig