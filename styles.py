STYLES_DARK = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

:root {
    --bg: #0a0a0a;
    --bg-card: #111;
    --border: #1e1e1e;
    --border-subtle: #1a1a1a;
    --text: #e5e5e5;
    --text-muted: #555;
    --text-dim: #3a3a3a;
    --spread-color: #e05a5a;
    --na: #2a2a2a;
}

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: var(--bg);
    color: var(--text);
}
h1, h2, h3 { font-family: 'Syne', sans-serif; }
.stApp { background-color: var(--bg); }

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
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
}

.market-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 12px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1px;
    margin-bottom: 16px;
}
.market-open    { background: #001a0a; border: 1px solid #4ade80; color: #4ade80; }
.market-closed  { background: #1a0a00; border: 1px solid #f97316; color: #f97316; }
.market-weekend { background: #0a0a1a; border: 1px solid #60a5fa; color: #60a5fa; }
.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.dot-open    { background: #4ade80; box-shadow: 0 0 6px #4ade80; animation: pulse 2s infinite; }
.dot-closed  { background: #f97316; }
.dot-weekend { background: #60a5fa; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.card {
    padding: 20px 24px;
    border-radius: 4px;
    background-color: var(--bg-card);
    border: 1px solid var(--border);
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
    color: var(--text);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.price-row { display: flex; gap: 32px; margin-bottom: 10px; }
.price-label {
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.price-value { font-size: 26px; font-weight: 500; color: #f0f0f0; }
.price-value span { font-size: 12px; color: var(--text-muted); margin-right: 2px; }
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
.spread { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.spread b { color: var(--spread-color); }
.summary-row { display: flex; gap: 16px; margin: 20px 0; }
.summary-pill { padding: 10px 18px; border-radius: 4px; font-size: 13px; font-weight: 500; }
.summary-pill.buy  { background: #1a1400; border: 1px solid #f5c842; color: #f5c842; }
.summary-pill.sell { background: #001a0a; border: 1px solid #4ade80; color: #4ade80; }
.na { color: var(--na) !important; }
hr { border-color: var(--border-subtle); }
.section-label {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #333;
    margin-bottom: 16px;
}

.stTabs [data-baseweb="tab"] {
    color: #e5e5e5 !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #e5e5e5 !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background-color: #f5c842 !important;
}

</style>
"""

STYLES_LIGHT = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

:root {
    --bg: #f5f5f0;
    --bg-card: #ffffff;
    --border: #e0e0d8;
    --border-subtle: #ececec;
    --text: #1a1a1a;
    --text-muted: #888;
    --text-dim: #bbb;
    --spread-color: #e05a5a;
    --na: #ccc;
}

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: var(--bg);
    color: var(--text);
}
h1, h2, h3 { font-family: 'Syne', sans-serif; }
.stApp { background-color: var(--bg) !important; }

.header-bar {
    border-bottom: 1px solid #ddd;
    padding-bottom: 12px;
    margin-bottom: 24px;
}
.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #b8960a;
}
.header-sub {
    font-size: 12px;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
}

.market-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 12px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1px;
    margin-bottom: 16px;
}
.market-open    { background: #f0fff5; border: 1px solid #4ade80; color: #16a34a; }
.market-closed  { background: #fff7f0; border: 1px solid #f97316; color: #c2510a; }
.market-weekend { background: #f0f5ff; border: 1px solid #60a5fa; color: #2563eb; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot-open    { background: #4ade80; box-shadow: 0 0 6px #4ade80; animation: pulse 2s infinite; }
.dot-closed  { background: #f97316; }
.dot-weekend { background: #60a5fa; }

.stCaption, [data-testid="stCaptionContainer"] p {
    color: #000000 !important;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.card {
    padding: 20px 24px;
    border-radius: 4px;
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid #ccc;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: border-color 0.2s;
}
.card.best-buy  { border-left-color: #b8960a; }
.card.best-sell { border-left-color: #16a34a; }
.card.both      { border-left-color: #2563eb; }

.bank-name {
    font-family: 'Syne', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.price-row { display: flex; gap: 32px; margin-bottom: 10px; }
.price-label {
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.price-value { font-size: 26px; font-weight: 500; color: #1a1a1a; }
.price-value span { font-size: 12px; color: var(--text-muted); margin-right: 2px; }
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
.badge-buy  { background: #fef9e7; color: #b8960a; border: 1px solid #b8960a; }
.badge-sell { background: #f0fff5; color: #16a34a; border: 1px solid #16a34a; }
.spread { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
.spread b { color: var(--spread-color); }
.summary-row { display: flex; gap: 16px; margin: 20px 0; }
.summary-pill { padding: 10px 18px; border-radius: 4px; font-size: 13px; font-weight: 500; }
.summary-pill.buy  { background: #fef9e7; border: 1px solid #b8960a; color: #b8960a; }
.summary-pill.sell { background: #f0fff5; border: 1px solid #16a34a; color: #16a34a; }
.na { color: var(--na) !important; }
hr { border-color: var(--border-subtle); }
.section-label {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #aaa;
    margin-bottom: 16px;
}

/* Fix tab text color in light mode */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--bg);
}

.stTabs [data-baseweb="tab"] {
    color: #1a1a1a !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #1a1a1a !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #1a1a1a !important;
}

/* The active tab underline — make it gold to match your theme */
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #b8960a !important;
}

</style>
"""