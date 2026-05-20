import time
from threading import Lock
from datetime import datetime, timedelta, timezone

price_cache = {
    "data": None,
    "last_fetched": 0,
    "history": [],
}
cache_lock = Lock()

CACHE_TTL = 900  # 15 minutes in seconds

def get_malaysia_time():
    return datetime.now(timezone.utc) + timedelta(hours=8)


def should_fetch_new_prices():
    current_time = time.time()
    myt_now = get_malaysia_time()

    # 1. Weekend Check (0 = Mon, 5 = Sat, 6 = Sun)
    if myt_now.weekday() >= 5:
        print("[INFO] Weekend. No trading. Serving cache.")
        return False

    # 2. Business Hours Check (Before 8 AM or after 6 PM)
    if myt_now.hour < 8 or myt_now.hour >= 18:
        print("[INFO] Market closed. Serving cache.")
        return False

    # 3. Expiration Check (15 minutes = 900 seconds)
    if price_cache["data"] is None or (current_time - price_cache["last_fetched"]) > CACHE_TTL:
        return True

    return False


def update_cache(new_prices):
    myt_now = get_malaysia_time()
    current_time_str = myt_now.strftime("%H:%M")

    with cache_lock:
        price_cache["data"] = new_prices
        price_cache["last_fetched"] = time.time()
        price_cache["history"].append({
            "time": current_time_str,
            "prices": new_prices
        })
        if len(price_cache["history"]) > 100:
            price_cache["history"].pop(0)

    return current_time_str