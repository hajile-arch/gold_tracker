"""Run: python test_app.py"""
import threading
import time

import app
from cache import price_cache
from scrapers import parse_quote_time


def q(sell, buy, t):
    return {"selling": sell, "buying": buy, "time": t}


def test_parse_quote_time():
    labels = [
        "Effective On 12:10 pm, 27 Nov 2026, Friday",   # CIMB
        "Effective On 27/11/2026 12:59",                # UOB
        "Effective on 27 Nov 2026 11:31 AM",            # Maybank
        "Effective On 27 November 2026 01:00 PM",       # Pbe
        "Effective At 01:00:01 PM ON 27 NOV 2026",      # RHB
    ]
    for label in labels:
        dt, has_time = parse_quote_time(label)
        assert has_time and dt.date().isoformat() == "2026-11-27", label
    dt, has_time = parse_quote_time("Effective On 27-11-2026")  # HSBC
    assert not has_time and dt.day == 27
    assert parse_quote_time("N/A") is None


def test_stale_quote_cannot_win():
    prices = {
        "UOB": q(400.0, 500.0, "Effective On 27/11/2026 08:00"),          # cheapest, but 5h old
        "RHB": q(480.0, 470.0, "Effective At 01:00:01 PM ON 27 NOV 2026"),
        "HSBC": q(481.0, 462.0, "Effective On 27-11-2026"),               # same day, date only: fresh
        "Maybank": q(482.0, 463.0, "N/A"),                                # unknown time: kept
    }
    a = app.analyse(prices)
    assert a["stale"] == ["UOB"], a
    assert a["best_buy"] == "RHB" and a["best_sell"] == "RHB", a


def test_single_background_scrape_and_no_blocking():
    calls = []
    release = threading.Event()

    def slow_fetch():
        calls.append(1)
        release.wait(5)
        return {"RHB": q(480.0, 470.0, "N/A")}

    app.fetch_prices, app.save_prices = slow_fetch, lambda p: None
    price_cache.update(data=None, last_fetched=0, scraping=False)
    client = app.app.test_client()

    start = time.time()
    r1 = client.get("/")
    r2 = client.get("/")
    assert r1.status_code == r2.status_code == 503   # warming up, answered immediately
    assert time.time() - start < 1
    assert len(calls) == 1                            # second visitor did not start another scrape

    release.set()
    for _ in range(50):
        if not price_cache["scraping"]:
            break
        time.sleep(0.05)
    r3 = client.get("/")
    assert r3.status_code == 200 and r3.get_json()["analysis"]["best_buy"] == "RHB"


def test_market_signal():
    # 10 past days, selling 400..490, buying 380..470
    records = [{"date": f"2026-11-{d:02d}", "prices": {"RHB": q(400.0 + i * 10, 380.0 + i * 10, "N/A")}}
               for i, d in enumerate(range(10, 20))]
    today = "2026-11-27"
    records.append({"date": today, "prices": {"RHB": q(1.0, 1.0, "N/A")}})  # today ignored as history

    cheap = app.market_signal(records, {"RHB": q(395.0, 375.0, "N/A")}, today)
    assert cheap["buy"]["verdict"] == "good" and cheap["buy"]["better_days_pct"] == 0, cheap
    assert cheap["sell"]["verdict"] == "wait" and cheap["sell"]["days"] == 10, cheap

    pricey = app.market_signal(records, {"RHB": q(495.0, 475.0, "N/A")}, today)
    assert pricey["buy"]["verdict"] == "wait" and pricey["sell"]["verdict"] == "good", pricey

    few = app.market_signal(records[:3], {"RHB": q(450.0, 430.0, "N/A")}, today)
    assert few["buy"]["verdict"] == "not_enough_data", few


def test_analytics_and_forecast():
    # Mon 2 Nov .. Fri 13 Nov 2026 weekdays, selling rises exactly RM 1/calendar day
    days = [d for d in range(2, 14) if d not in (7, 8)]
    records = [{"date": f"2026-11-{d:02d}", "prices": {
        "UOB": q(500.0 + d, 495.0 + d, "N/A"),
        "RHB": q(510.0 + d, 480.0 + d, "N/A"),
        "CIMB": q(505.0 + d, 490.0 + d, "N/A"),
        "HSBC": q(505.0 + d, 488.0 + d, "N/A"),
    }} for d in days]
    records[3]["prices"]["UOB"] = q(700.0, 695.0, "N/A")  # scraper glitch on 5 Nov

    a = app.analytics(records)
    assert a["days"] == 10 and a["best_buy_day"]["date"] == "2026-11-02", a
    assert a["banks"]["UOB"]["cheapest_pct"] == 90, a["banks"]          # glitch snapshot ignored
    assert a["banks"]["UOB"]["avg_spread_pct"] < a["banks"]["RHB"]["avg_spread_pct"]

    fc = a["forecast"]
    assert fc["slope_per_day"] == 1.0, fc
    assert [p["date"] for p in fc["points"]] == ["2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"]
    assert fc["points"][0]["price"] == 521.0, fc                       # median sell 505+16, weekends skipped
    assert app.forecast({"2026-11-02": 1.0}) is None                   # too little data

    assert a["moves"][0]["date"] == "2026-11-09" and a["moves"][0]["prev"] == "2026-11-06", a["moves"]  # RM 3 over weekend
    assert app.biggest_moves({"2026-08-01": 100, "2026-08-20": 200}, ["2026-08-01", "2026-08-20"]) == []  # data gap
    assert app.analytics([]) == {"days": 0}


if __name__ == "__main__":
    test_analytics_and_forecast()
    test_market_signal()
    test_parse_quote_time()
    test_stale_quote_cannot_win()
    test_single_background_scrape_and_no_blocking()
    print("all checks passed")
