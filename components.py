import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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


def render_card(col, bank, info, is_buy, is_sell):
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


def render_summary(best_buy, best_sell):
    if best_buy or best_sell:
        st.markdown(f"""
        <div class="summary-row">
            <div class="summary-pill buy">💡 Best to BUY &nbsp;·&nbsp; {best_buy}</div>
            <div class="summary-pill sell">💰 Best to SELL &nbsp;·&nbsp; {best_sell}</div>
        </div>
        """, unsafe_allow_html=True)


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
        st.plotly_chart(_make_chart(df, sell_cols, light_mode), use_container_width=True,theme=None)
    with tab_buy:
        st.plotly_chart(_make_chart(df, buy_cols, light_mode), use_container_width=True,theme=None)
    with tab_all:
        st.plotly_chart(_make_chart(df, sell_cols + buy_cols, light_mode), use_container_width=True,theme=None)

    csv_data = df.to_csv().encode("utf-8")
    import time
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"gold_prices_{time.strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )


def _make_chart(df, cols_to_plot, light_mode=False):
    bg = "#f5f5f0" if light_mode else "#0a0a0a"
    plot_bg = "#ffffff" if light_mode else "#0f0f0f"
    
    # This will now be accurately applied!
    font_color = "#1a1a1a" if light_mode else "#e5e5e5" 
    
    grid_color = "#e0e0d8" if light_mode else "#1a1a1a"
    legend_bg = "#ffffff" if light_mode else "#0a0a0a"
    legend_border = "#e0e0d8" if light_mode else "#1e1e1e"
    
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