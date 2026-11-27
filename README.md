# 🥇 Gold Tracker MY

A real-time gold price dashboard that scrapes and compares gold prices across Malaysian banks, helping you find the best place to buy or sell.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-deployed-ff4b4b)

## Features

- 📊 **Live price comparison** — CIMB, UOB, Maybank, Public Bank, RHB, HSBC
- 🏆 **Smart recommendations** — highlights best bank to buy and best bank to sell (outdated quotes are skipped)
- 📈 **Price trend chart** — tracks selling & buying prices throughout the day
- 🌗 **Dark / light mode** — toggle between themes
- 📥 **CSV export** — download today's price history
- 🕐 **Market status** — shows whether Malaysian gold market is open, closed, or weekend
- ⚡ **Auto-refresh** — an open tab re-fetches prices every 15 minutes

## Tech Stack

- **Python** — scraping, data processing
- **BeautifulSoup** — web scraping from bank websites
- **Streamlit** — live dashboard UI
- **Plotly** — interactive price trend charts
- **Flask** — API backend
- **Selenium** — scrapes Public Bank (needs Chrome)
- **MongoDB** — stores price history

## Project Structure

```
gold_tracker/
├── dashboard.py       # Streamlit app entry point
├── api_clients.py     # Fetches prices & history from backend
├── components.py      # UI components (cards, chart, summary)
├── styles.py          # Dark & light mode CSS
├── app.py             # Flask API server
├── scrapers.py        # One scraper per bank
├── cache.py           # In-memory price cache + Malaysia time
├── database.py        # MongoDB history storage
└── config.py          # Bank URLs, request headers, settings
```

## Run Locally

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Create a `.env` file** (only needed for the Flask API)
```
MONGODB_URI=mongodb+srv://...   # price history
SCRAPER_API_KEY=...             # scrape.do proxy, used for Maybank
```

**3. Start the Flask API**
```bash
python app.py
```

**4. Launch the dashboard against your local API**
```bash
# macOS / Linux
API_URL=http://localhost:10000 streamlit run dashboard.py
# Windows PowerShell
$env:API_URL="http://localhost:10000"; streamlit run dashboard.py
```

Without `API_URL`, the dashboard uses the deployed API on Render, so you can run just step 4 to work on the UI.

Then open [http://localhost:8501](http://localhost:8501)

## API

| Endpoint | Description |
|----------|-------------|
| `GET /` | Latest prices for all banks, plus best buy/sell and any outdated quotes |
| `GET /signal` | Buy/sell signal: today's price vs the last 30 days in MongoDB |
| `GET /analytics?days=90` | Daily trend, best buy/sell day, bank leaderboard and a 5-day straight-line forecast |
| `GET /history/all` | Today's price history (from MongoDB) |
| `GET /history` | Prices collected since the server started (in memory) |
| `GET /auto_collect` | Starts a background scrape during market hours (for a cron job) |
| `GET /keepalive` | Health check |

## Live Demo

> Deployed on Streamlit Cloud — https://trackthegold.streamlit.app
