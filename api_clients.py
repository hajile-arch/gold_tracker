import os
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import requests

# Set API_URL=http://localhost:10000 to use a locally running app.py
API_URL = os.environ.get("API_URL", "https://just-basic-gold-tracking.onrender.com")
REFRESH_INTERVAL = 15 * 60


def fetch_prices():
    r = requests.get(API_URL, timeout=60)
    r.raise_for_status()
    return r.json()


def fetch_history():
    r = requests.get(f"{API_URL}/history/all", timeout=15)
    r.raise_for_status()
    return r.json()


def fetch_signal():
    r = requests.get(f"{API_URL}/signal", timeout=15)
    r.raise_for_status()
    return r.json()


NEWS_QUERY = "gold price (fed OR dollar OR rally OR slump OR falls OR rises OR record)"


def fetch_news(after, before, limit=5):
    """Gold headlines published between two YYYY-MM-DD dates, from Google News RSS."""
    r = requests.get("https://news.google.com/rss/search",
                     params={"q": f"{NEWS_QUERY} after:{after} before:{before}",
                             "hl": "en-MY", "gl": "MY", "ceid": "MY:en"},
                     headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    r.raise_for_status()
    news = []
    for item in list(ET.fromstring(r.content).iter("item"))[:limit]:
        source = item.findtext("source", "")
        news.append({
            "title": item.findtext("title", "").removesuffix(f" - {source}"),
            "link": item.findtext("link"),
            "source": source,
            "date": parsedate_to_datetime(item.findtext("pubDate")).strftime("%d %b"),
        })
    return news


def fetch_analytics(days=90):
    r = requests.get(f"{API_URL}/analytics", params={"days": days}, timeout=30)
    r.raise_for_status()
    return r.json()
