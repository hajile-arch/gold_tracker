# 🥇 Gold Tracker MY

A real-time gold price dashboard that scrapes and compares gold prices across Malaysian banks, helping you find the best place to buy or sell.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-deployed-ff4b4b)

## Features

- 📊 **Live price comparison** — CIMB, UOB, Maybank, Public Bank, RHB, HSBC
- 🏆 **Smart recommendations** — highlights best bank to buy and best bank to sell
- 📈 **Price trend chart** — tracks selling & buying prices throughout the day
- 🌗 **Dark / light mode** — toggle between themes
- 📥 **CSV export** — download today's price history
- 🕐 **Market status** — shows whether Malaysian gold market is open, closed, or weekend
- ⚡ **Auto-refresh** — prices update automatically on a set interval

## Tech Stack

- **Python** — scraping, data processing
- **BeautifulSoup** — web scraping from bank websites
- **Streamlit** — live dashboard UI
- **Plotly** — interactive price trend charts
- **Flask** — API backend (`/gold` endpoint)

## Project Structure

```
gold_tracker/
├── dashboard.py       # Streamlit app entry point
├── api_clients.py     # Fetches prices & history from backend
├── components.py      # UI components (cards, chart, summary)
├── styles.py          # Dark & light mode CSS
└── app.py             # Flask API server
```

## Run Locally

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Start the Flask API**
```bash
python app.py
```

**3. Launch the dashboard**
```bash
streamlit run dashboard.py
```

Then open [http://localhost:8501](http://localhost:8501)

## API

| Endpoint | Description |
|----------|-------------|
| `GET /gold` | Returns latest gold prices for all banks |
| `GET /history` | Returns price history for today |

## Live Demo

> Deployed on Streamlit Cloud — [add your link here]
