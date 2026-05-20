STYLES = """
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
"""