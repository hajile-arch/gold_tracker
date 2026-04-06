from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import urllib3

app = Flask(__name__)



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
SCRAPER_API_KEY = "0546a9c94f1646fa8c1f5eb0a374e9499afb9e38299"
proxyModeUrl = "http://{}:@proxy.scrape.do:8080".format(SCRAPER_API_KEY)
proxies = {
    "http": proxyModeUrl,
    "https": proxyModeUrl,
}
response = requests.request("GET", may_url, proxies=proxies, verify=False)
print(response.text)

def get_maybank(session):
    try:
        res = session.get(
            may_url,
            headers=headers,
            proxies=proxies,   # <-- use the proxy
            verify=False,
            timeout=20
        )
        print("[DEBUG] Maybank status:", res.status_code)
        print("[DEBUG] Maybank HTML length:", len(res.text))
        print("[DEBUG] Maybank snippet:", res.text[:500])  # see what came back
        return res
    except Exception as e:
        print(f"[ERROR] Maybank request failed: {e}")
        return None

def safe_request(session, url):
    try:
        return session.get(url, headers=headers, timeout=8)
    except Exception as e:
        print(f"[ERROR] Request failed for {url}: {e}")
        return None


def fetch_prices():
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
        res = safe_request(session, may_url)
        if res:
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
        

    return gold_prices


@app.route("/")
def gold():
    data = fetch_prices()

    # ---------------- FILTER VALID DATA ----------------
    valid = {
        k: v for k, v in data.items()
        if v["selling"] is not None and v["buying"] is not None
    }

    # ---------------- ANALYSIS ----------------
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

    # fallback if everything fails
    return jsonify({
        "prices": data,
        "analysis": "No valid data available"
    })


if __name__ == "__main__":

    # Test Maybank proxy response before starting server
    print("[TEST] Fetching Maybank via proxy...")
    response = requests.get(may_url, proxies=proxies, verify=False, timeout=20)
    print("[TEST] Status:", response.status_code)
    print("[TEST] Response:", response.text[:1000])


    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)