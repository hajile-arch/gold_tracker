import requests

API_URL = "https://just-basic-gold-tracking.onrender.com"
REFRESH_INTERVAL = 15 * 60


def fetch_prices():
    r = requests.get(API_URL, timeout=60)
    r.raise_for_status()
    return r.json()


def fetch_history():
    r = requests.get(f"{API_URL}/history/all", timeout=15)
    r.raise_for_status()
    return r.json()