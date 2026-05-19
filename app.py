import time
import threading
import os
from flask import Flask, jsonify

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from cache import price_cache, cache_lock, should_fetch_new_prices, update_cache, get_malaysia_time
from database import save_prices, get_history_today
from scrapers import fetch_prices

app = Flask(__name__)


def run_fetch_and_cache():
    new_prices = fetch_prices()
    current_time_str = update_cache(new_prices)
    save_prices(new_prices)
    print(f"[LOG] Background fetch complete at {current_time_str}")


@app.route("/auto_collect")
def auto_collect():
    myt_now = get_malaysia_time()

    if myt_now.weekday() < 5 and 8 <= myt_now.hour < 18:
        with cache_lock:
            if should_fetch_new_prices():
                print(f"[LOG] Cron triggered auto-collect at {myt_now.strftime('%H:%M')}!")
                threading.Thread(target=run_fetch_and_cache, daemon=True).start()
                return "Scrape started in background", 200
            else:
                return "Ignored (Cache still valid)", 200

    return "Ignored (Market Closed)", 200


@app.route("/history")
def history():
    return jsonify(price_cache["history"])


@app.route("/history/all")
def history_all():
    return jsonify(get_history_today())


@app.route("/keepalive")
def keepalive():
    return "Server is awake!", 200


@app.route("/")
def gold():
    with cache_lock:
        if should_fetch_new_prices():
            print(f"[LOG] SCRAPE TRIGGERED AT {get_malaysia_time().strftime('%H:%M:%S')}!", flush=True)
            print("[INFO] Fetching fresh prices...", flush=True)
            price_cache["data"] = fetch_prices()
            price_cache["last_fetched"] = time.time()
            save_prices(price_cache["data"])
        else:
            time_left = (900 - (time.time() - price_cache["last_fetched"])) / 60
            print(f"[INFO] Serving from cache. Next check allowed in {time_left:.1f} minutes.")

    data = price_cache["data"]

    # Fallback safety net
    if data is None:
        with cache_lock:
            if price_cache["data"] is None:
                print("[INFO] Cache empty on first load, fetching once...")
                price_cache["data"] = fetch_prices()
                price_cache["last_fetched"] = time.time()
                save_prices(price_cache["data"])
            data = price_cache["data"]

    valid = {k: v for k, v in data.items() if v["selling"] is not None and v["buying"] is not None}

    if valid:
        best_buy = min(valid.items(), key=lambda x: x[1]["selling"])
        best_sell = max(valid.items(), key=lambda x: x[1]["buying"])
        return jsonify({
            "prices": data,
            "analysis": {
                "best_buy": best_buy[0],
                "best_sell": best_sell[0]
            }
        })

    return jsonify({"prices": data, "analysis": "No valid data available"})


if __name__ == "__main__":
    print("[INFO] Starting server...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)