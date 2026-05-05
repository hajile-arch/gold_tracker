import time

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import urllib3
from dotenv import load_dotenv
from threading import Lock
from datetime import datetime, timedelta, timezone
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# --- GLOBAL CACHE VARIABLES ---
price_cache = {
    "data": None,
    "last_fetched": 0
}
cache_lock = Lock()

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
    if price_cache["data"] is None or (current_time - price_cache["last_fetched"]) > 900:
        return True
        
    return False

uob_url = "https://www.uob.com.my/wsm/stayinformed.do?path=gia"
cimb_url = "https://www.cimb.com.my/en/personal/wealth-management/investments/investment-products/e-gold-investment-account-egia.html"
may_url = "https://www.maybank2u.com.my/maybank2u/malaysia/en/personal/rates/gold_and_silver.page"
pbe_url = "https://www.pbebank.com/en/invest/gold-egold-investment-account/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
    "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/"
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
# SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
# proxyModeUrl = "http://{}:@proxy.scrape.do:8080".format(SCRAPER_API_KEY)
# proxies = {
#     "http": proxyModeUrl,
#     "https": proxyModeUrl,
# }




def safe_request(session, url):
    try:
        return session.get(url, headers=headers, timeout=8)
    except Exception as e:
        print(f"[ERROR] Request failed for {url}: {e}")
        return None

def safe_request_proxy(url):
    """For sites that block datacenter IPs (e.g. Maybank)"""
    try:
        api_key = os.environ.get("SCRAPER_API_KEY")  # ← read at call time
        if not api_key:
            print("[ERROR] SCRAPER_API_KEY is not set")
            return None
        
        proxy_url = "http://{}:@proxy.scrape.do:8080".format(api_key)
        proxies = {"http": proxy_url, "https": proxy_url}
        
        return requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=30)
    except Exception as e:
        print(f"[ERROR] Proxy request failed for {url}: {e}")
        return None

def fetch_prices():
    print("[DEBUG] fetch_prices() called!")
    session = requests.Session()

    # ---------------- DEFAULT STRUCTURE ----------------
    gold_prices = {
        "CIMB": {"selling": None, "buying": None, "time": "N/A"},
        "UOB": {"selling": None, "buying": None, "time": "N/A"},
        "Maybank": {"selling": None, "buying": None, "time": "N/A"},
        "Pbe":{"selling": None, "buying": None, "time": "N/A"}
    }

    # ---------------- CIMB ----------------
    try:
        res = safe_request(session, cimb_url)
        if res:
            soup = BeautifulSoup(res.text, "html.parser")

            time_cimb = soup.find(string=lambda t: t and "Last Updated" in t)

            for table in soup.find_all("table"):
                for row in table.find_all("tr"):
                    cols = [c.text.strip() for c in row.find_all(["td", "th"])]
                    if len(cols) == 3 and cols[0] == "CIMB Clicks":
                        gold_prices["CIMB"]["selling"] = float(cols[1])
                        gold_prices["CIMB"]["buying"] = float(cols[2])

            if time_cimb:
                gold_prices["CIMB"]["time"] = str(time_cimb)

    except Exception as e:
        print("[ERROR] CIMB parsing failed:", e)

    # ---------------- UOB (MOST RELIABLE) ----------------
    try:
        res = safe_request(session, uob_url)
        if res:
            for line in res.text.split("\n"):
                cols = line.split(",")
                if cols[0] == "GOLD SAVINGS ACCOUNT":
                    gold_prices["UOB"]["selling"] = float(cols[2])
                    gold_prices["UOB"]["buying"] = float(cols[3])
                    gold_prices["UOB"]["time"] = cols[5]

    except Exception as e:
        print("[ERROR] UOB parsing failed:", e)

    # ---------------- MAYBANK (UNRELIABLE ON CLOUD) ----------------
    try:
        res = safe_request_proxy(may_url)  # ← proxy used here
        if res:
            print("[DEBUG] Maybank status:", res.status_code)
            soup = BeautifulSoup(res.text, "html.parser")
            time_may = soup.find(string=lambda t: t and "Effective on" in t)
            tables = soup.find_all("table")
            if tables:
                td = tables[0].find_all("td")
                if len(td) >= 3:
                    gold_prices["Maybank"]["selling"] = float(td[1].text.strip())
                    gold_prices["Maybank"]["buying"] = float(td[2].text.strip())
            if time_may:
                gold_prices["Maybank"]["time"] = str(time_may)
    except Exception as e:
        print("[ERROR] Maybank parsing failed:", e)
    
    # ---------------- PBe (Public Bank) via Selenium ----------------
    try:
        # 1. Setup Cloud-Safe Chrome Options
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Run invisibly (Crucial for Render)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox") # Bypass OS security model (Crucial for Render)
        chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems

        # 2. Run your scraper
        with webdriver.Chrome(options=chrome_options) as driver:
            driver.get("https://www.pbebank.com/en/invest/gold-egold-investment-account/")
            driver.implicitly_wait(10)

            # Grab the text exactly as you wrote it
            selling_text = driver.find_element(By.XPATH,"//td[contains(text(), '1 gram')]/following-sibling::td[1]").get_attribute("textContent").strip()
            buying_text = driver.find_element(By.XPATH,"//td[contains(text(), '1 gram')]/following-sibling::td[2]").get_attribute("textContent").strip()
            time_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Gold Investment Account as at')]").get_attribute("textContent").strip()
            print("[DEBUG] PBe time_element raw:", repr(time_element))  # ADD THIS
            

            gold_prices["Pbe"]["selling"] = float(selling_text)
            gold_prices["Pbe"]["buying"] = float(buying_text)
            gold_prices["Pbe"]["time"] = time_element
            print("[DEBUG] PBe full result:", gold_prices["Pbe"])  # ADD THIS
    except Exception as e:
        print(f"[ERROR] PBe parsing failed: {e}")

    return gold_prices

@app.route("/keepalive")
def keepalive():
    return "Server is awake!", 200

@app.route("/")
def gold():
    with cache_lock: # Lock the door!
        if should_fetch_new_prices():
            print("[INFO] Fetching fresh prices...")
            price_cache["data"] = fetch_prices()
            price_cache["last_fetched"] = time.time()
        else:
            time_left = (900 - (time.time() - price_cache["last_fetched"])) / 60
            print(f"[INFO] Serving from cache. Next check allowed in {time_left:.1f} minutes.")

    data = price_cache["data"]

    # Fallback safety net
    if data is None:
        with cache_lock:
            if price_cache["data"] is None:
                print("[INFO] Cache empty on first load, fetching once...")  # ADD THIS
                price_cache["data"] = fetch_prices()
                price_cache["last_fetched"] = time.time()
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

    # Test Maybank proxy response before starting server
    # print("[TEST] Fetching Maybank via proxy...")
    # response = requests.get(may_url, proxies=proxies, verify=False, timeout=20)
    # print("[TEST] Status:", response.status_code)
    # print("[TEST] Response:", response.text[:1000])

    print("[INFO] Starting server...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)