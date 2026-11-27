import threading
import os
from datetime import date, timedelta
from statistics import mean, median, linear_regression, stdev
from flask import Flask, jsonify, request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from cache import price_cache, cache_lock, should_fetch_new_prices, update_cache, get_malaysia_time
from config import STALE_HOURS, SIGNAL_DAYS, SIGNAL_MIN_DAYS, OUTLIER_PCT, FORECAST_LOOKBACK
from database import save_prices, get_history_today, get_history_since
from scrapers import fetch_prices, parse_quote_time

app = Flask(__name__)


def run_fetch_and_cache():
    try:
        new_prices = fetch_prices()
        current_time_str = update_cache(new_prices)
        save_prices(new_prices)
        print(f"[LOG] Background fetch complete at {current_time_str}")
    finally:
        with cache_lock:
            price_cache["scraping"] = False


def start_scrape_if_needed():
    """Start one background scrape if the cache is due. Never blocks on the scrape itself."""
    with cache_lock:
        if price_cache["scraping"] or not should_fetch_new_prices():
            return False
        price_cache["scraping"] = True
    print(f"[LOG] SCRAPE TRIGGERED AT {get_malaysia_time().strftime('%H:%M:%S')}!", flush=True)
    threading.Thread(target=run_fetch_and_cache, daemon=True).start()
    return True


def find_stale(prices):
    """Banks whose quote is more than STALE_HOURS older than the newest quote."""
    parsed = {bank: parse_quote_time(info.get("time")) for bank, info in prices.items()}
    timed = [p[0] for p in parsed.values() if p and p[1]]
    if not timed:
        return []
    newest = max(timed)
    stale = []
    for bank, p in parsed.items():
        if not p:
            continue  # unknown time: don't punish it
        dt, has_time = p
        if has_time:
            is_stale = newest - dt > timedelta(hours=STALE_HOURS)
        else:
            is_stale = dt.date() < newest.date()  # date-only quote (HSBC)
        if is_stale:
            stale.append(bank)
    return stale


def analyse(prices):
    stale = find_stale(prices)
    valid = {k: v for k, v in prices.items()
             if v["selling"] is not None and v["buying"] is not None and k not in stale}
    if not valid:
        return "No valid data available"
    return {
        "best_buy": min(valid, key=lambda k: valid[k]["selling"]),
        "best_sell": max(valid, key=lambda k: valid[k]["buying"]),
        "stale": stale,
    }


def market_price(prices, field):
    """Median across banks, so one odd/outdated bank doesn't skew it."""
    vals = [v[field] for v in prices.values() if v.get(field) is not None]
    return median(vals) if vals else None


def daily_prices(records, field):
    by_day = {}
    for r in records:
        p = market_price(clean_quotes(r.get("prices") or {}), field)
        if p is not None:
            by_day.setdefault(r["date"], []).append(p)
    return {d: mean(v) for d, v in by_day.items()}


def market_signal(records, current, today):
    """Compare today's market price against past days' averages.

    selling = what you pay the bank (low is good for buying)
    buying  = what the bank pays you (high is good for selling)
    """
    current = {k: v for k, v in current.items() if k not in find_stale(current)}
    result = {}
    for field, action in (("selling", "buy"), ("buying", "sell")):
        past = daily_prices(records, field)
        past.pop(today, None)  # today is "now", not history
        now = market_price(current, field)
        if len(past) < SIGNAL_MIN_DAYS or now is None:
            result[action] = {"verdict": "not_enough_data", "days": len(past)}
            continue
        vals = list(past.values())
        # % of past days that were better for you than right now
        if action == "buy":
            better = sum(p < now for p in vals)
        else:
            better = sum(p > now for p in vals)
        pct = round(better / len(vals) * 100)
        verdict = "good" if pct <= 25 else "wait" if pct >= 75 else "neutral"
        result[action] = {
            "verdict": verdict,
            "better_days_pct": pct,
            "now": round(now, 2),
            "avg": round(mean(vals), 2),
            "low": round(min(vals), 2),
            "high": round(max(vals), 2),
            "days": len(vals),
        }
    return result


def clean_quotes(prices):
    """Complete quotes only, minus any more than OUTLIER_PCT off the snapshot median (scraper glitches)."""
    ok = {k: v for k, v in prices.items() if v.get("selling") and v.get("buying")}
    if not ok:
        return {}
    mid = {f: median(v[f] for v in ok.values()) for f in ("selling", "buying")}
    return {k: v for k, v in ok.items()
            if all(abs(v[f] - mid[f]) / mid[f] * 100 <= OUTLIER_PCT for f in mid)}


def forecast(daily, days_ahead=5):
    """Straight-line trend through the last FORECAST_LOOKBACK days, projected over the next trading days."""
    # ponytail: linear trend + 2x residual band, a rough guide not a model; band understates real risk
    dates = sorted(daily)[-FORECAST_LOOKBACK:]
    if len(dates) < SIGNAL_MIN_DAYS:
        return None
    d0 = date.fromisoformat(dates[0])
    x = [(date.fromisoformat(d) - d0).days for d in dates]
    y = [daily[d] for d in dates]
    slope, intercept = linear_regression(x, y)
    band = 2 * stdev(yi - (slope * xi + intercept) for xi, yi in zip(x, y))
    points, day = [], date.fromisoformat(dates[-1])
    while len(points) < days_ahead:
        day += timedelta(days=1)
        if day.weekday() >= 5:
            continue
        p = slope * (day - d0).days + intercept
        points.append({"date": day.isoformat(), "price": round(p, 2),
                       "low": round(p - band, 2), "high": round(p + band, 2)})
    return {"slope_per_day": round(slope, 2), "lookback_days": len(dates), "points": points}


def analytics(records):
    sell, buy = daily_prices(records, "selling"), daily_prices(records, "buying")
    if not sell:
        return {"days": 0}
    banks, snapshots = {}, 0
    for r in records:
        q = clean_quotes(r.get("prices") or {})
        if not q:
            continue
        snapshots += 1
        for k, v in q.items():
            banks.setdefault(k, {"spreads": [], "cheapest": 0, "best_sell": 0})
            banks[k]["spreads"].append((v["selling"] - v["buying"]) / v["selling"] * 100)
        banks[min(q, key=lambda k: q[k]["selling"])]["cheapest"] += 1
        banks[max(q, key=lambda k: q[k]["buying"])]["best_sell"] += 1

    dates = sorted(sell)
    best_buy = min(sell, key=sell.get)
    best_sell = max(buy, key=buy.get)
    return {
        "days": len(dates),
        "daily": [{"date": d, "sell": round(sell[d], 2), "buy": round(buy.get(d, sell[d]), 2)} for d in dates],
        "change_pct": round((sell[dates[-1]] / sell[dates[0]] - 1) * 100, 2),
        "best_buy_day": {"date": best_buy, "price": round(sell[best_buy], 2)},
        "best_sell_day": {"date": best_sell, "price": round(buy[best_sell], 2)},
        "banks": {k: {"avg_spread_pct": round(mean(b["spreads"]), 2),
                      "cheapest_pct": round(b["cheapest"] / snapshots * 100),
                      "best_sell_pct": round(b["best_sell"] / snapshots * 100)}
                  for k, b in banks.items()},
        "forecast": forecast(sell),
        "moves": biggest_moves(sell, dates),
    }


def biggest_moves(sell, dates, n=3):
    """Largest day-to-day % changes, skipping jumps across data gaps longer than a weekend."""
    moves = [{"date": d, "prev": p, "pct": round((sell[d] / sell[p] - 1) * 100, 2)}
             for p, d in zip(dates, dates[1:])
             if (date.fromisoformat(d) - date.fromisoformat(p)).days <= 4]
    return sorted(moves, key=lambda m: abs(m["pct"]), reverse=True)[:n]


@app.route("/analytics")
def analytics_route():
    days = min(max(request.args.get("days", 90, type=int), 1), 365)
    return jsonify(analytics(get_history_since(days)))


@app.route("/signal")
def signal():
    data = price_cache["data"]
    if data is None:
        return jsonify({"error": "Warming up"}), 503
    today = get_malaysia_time().strftime("%Y-%m-%d")
    return jsonify(market_signal(get_history_since(SIGNAL_DAYS), data, today))


@app.route("/auto_collect")
def auto_collect():
    myt_now = get_malaysia_time()

    if myt_now.weekday() < 5 and 8 <= myt_now.hour < 18:
        if start_scrape_if_needed():
            return "Scrape started in background", 200
        return "Ignored (Cache still valid or scrape already running)", 200

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
    start_scrape_if_needed()
    data = price_cache["data"]

    if data is None:
        # First scrape after a cold start is still running; don't make the visitor wait on it.
        return jsonify({"error": "Warming up, prices are being fetched. Try again in a minute."}), 503

    return jsonify({"prices": data, "analysis": analyse(data)})


if __name__ == "__main__":
    print("[INFO] Starting server...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
